#!/usr/bin/env python
# encoding: utf-8

'''
Bitcoin protocol access for Bitnodes.
Reference: https://en.bitcoin.it/wiki/Protocol_specification

-------------------------------------------------------------------------------
                     PACKET STRUCTURE FOR BITCOIN PROTOCOL
                           protocol version >= 70001
-------------------------------------------------------------------------------
[---MESSAGE---]
[ 4] MAGIC_NUMBER               (\xF9\xBE\xB4\xD9)                  uint32_t
[12] COMMAND                                                        char[12]
[ 4] LENGTH                     <I (len(payload))                   uint32_t
[ 4] CHECKSUM                   (sha256(sha256(payload))[:4])       uint32_t
[..] PAYLOAD                    see below

    [---VERSION_PAYLOAD---]
    [ 4] VERSION                <i                                  int32_t
    [ 8] SERVICES               <Q                                  uint64_t
    [ 8] TIMESTAMP              <q                                  int64_t
    [26] ADDR_RECV
        [ 8] SERVICES           <Q                                  uint64_t
        [16] IP_ADDR
            [12] IPV6           (\x00 * 10 + \xFF * 2)              char[12]
            [ 4] IPV4                                               char[4]
        [ 2] PORT               >H                                  uint16_t

    [---ADDR_PAYLOAD---]
    [..] COUNT                  variable integer
    [..] ADDR_LIST              multiple of COUNT (max 1000)
        [ 4] TIMESTAMP          <I                                  uint32_t
        [ 8] SERVICES           <Q                                  uint64_t
        [16] IP_ADDR
            [12] IPV6           (\x00 * 10 + \xFF * 2)              char[12]
            [ 4] IPV4                                               char[4]
        [ 2] PORT               >H                                  uint16_t
'''


import socket
import socks
import time
import struct
import hashlib
import random
from cStringIO import StringIO
from operator import itemgetter

HEADER_LEN = 24
MAGIC_NUMBER = "\xF9\xBE\xB3\xD5"
SOCKET_BUFSIZE = 8192

# This is set prior to throwing PayloadTooShortError exception to
# allow caller to fetch more data over the network.
required_len = 0

class PayloadTooShortError(Exception):
    pass


def sha256(data):
        return hashlib.sha256(data).digest()


def unpack(fmt, string):
    # Wraps problematic struct.unpack() in a try statement
    return struct.unpack(fmt, string)[0]


def serialize_network_address(addr):
        network_address = []
        if len(addr) == 4:
            (timestamp, services, ip_address, port) = addr
            network_address.append(struct.pack("<I", timestamp))
        else:
            (services, ip_address, port) = addr
        network_address.append(struct.pack("<Q", services))
        if ip_address.endswith(".onion"):
            # convert .onion address to its ipv6 equivalent (6 + 10 bytes)
            network_address.append(
                ONION_PREFIX + b32decode(ip_address[:-6], True))
        elif "." in ip_address:
            # unused (12 bytes) + ipv4 (4 bytes) = ipv4-mapped ipv6 address
            unused = "\x00" * 10 + "\xFF" * 2
            network_address.append(
                unused + socket.inet_pton(socket.AF_INET, ip_address))
        else:
            # ipv6 (16 bytes)
            network_address.append(
                socket.inet_pton(socket.AF_INET6, ip_address))
        network_address.append(struct.pack(">H", port))
        return ''.join(network_address)



def serialize_string(data):
        length = len(data)
        if length < 0xFD:
            return chr(length) + data
        elif length <= 0xFFFF:
            return chr(0xFD) + struct.pack("<H", length) + data
        elif length <= 0xFFFFFFFF:
            return chr(0xFE) + struct.pack("<I", length) + data
        return chr(0xFF) + struct.pack("<Q", length) + data


def serialize_version_payload(to_addr, from_addr):
        protocol_version = 70013
        from_services = 0
        user_agent = "/lbtcnodes/"
        height = 478000
        relay = 0  # set to 1 to receive all txs

        payload = [
            struct.pack("<i", protocol_version),
            struct.pack("<Q", from_services),
            struct.pack("<q", int(time.time())),
            serialize_network_address(to_addr),
            serialize_network_address(from_addr),
            struct.pack("<Q", random.getrandbits(64)),
            serialize_string(user_agent),
            struct.pack("<i", height),
            struct.pack("<?", relay),
        ]
        return ''.join(payload)


def serialize_ping_payload(nonce):
        payload = [
            struct.pack("<Q", nonce),
        ]
        return ''.join(payload)

def serialize_msg(**kwargs):
    command = kwargs['command']
    msg = [
        MAGIC_NUMBER,
        command + "\x00" * (12 - len(command)),
    ]

    payload = ""
    if command == "version":
        to_services = 1
        from_services = 0
        to_addr = (to_services,) + kwargs['to_addr']
        from_addr = (from_services,) + kwargs['from_addr']
        payload = serialize_version_payload(to_addr, from_addr)
    elif command == "ping" or command == "pong":
        nonce = kwargs['nonce']
        payload = serialize_ping_payload(nonce)

    msg.extend([
        struct.pack("<I", len(payload)),
        sha256(sha256(payload))[:4],
        payload,
    ])

    return ''.join(msg)


def deserialize_int(data):
        length = unpack("<B", data.read(1))
        if length == 0xFD:
            length = unpack("<H", data.read(2))
        elif length == 0xFE:
            length = unpack("<I", data.read(4))
        elif length == 0xFF:
            length = unpack("<Q", data.read(8))
        return length


def deserialize_string(data):
        length = deserialize_int(data)
        return data.read(length)


def deserialize_network_address(data, has_timestamp=False):
        timestamp = None
        if has_timestamp:
            timestamp = unpack("<I", data.read(4))

        services = unpack("<Q", data.read(8))

        _ipv6 = data.read(12)
        _ipv4 = data.read(4)
        port = unpack(">H", data.read(2))
        _ipv6 += _ipv4

        ipv4 = ""
        ipv6 = ""
        onion = ""

        ONION_PREFIX = "\xFD\x87\xD8\x7E\xEB\x43"  # ipv6 prefix for .onion address
        if _ipv6[:6] == ONION_PREFIX:
            onion = b32encode(_ipv6[6:]).lower() + ".onion"  # use .onion
        else:
            ipv6 = socket.inet_ntop(socket.AF_INET6, _ipv6)
            ipv4 = socket.inet_ntop(socket.AF_INET, _ipv4)
            if ipv4 in ipv6:
                ipv6 = ""  # use ipv4
            else:
                ipv4 = ""  # use ipv6

        return {
            'timestamp': timestamp,
            'services': services,
            'ipv4': ipv4,
            'ipv6': ipv6,
            'onion': onion,
            'port': port,
        }

def deserialize_version_payload(data):
        msg = {}
        data = StringIO(data)
        msg['version'] = unpack("<i", data.read(4))
        msg['services'] = unpack("<Q", data.read(8))
        msg['timestamp'] = unpack("<q", data.read(8))
        msg['to_addr'] = deserialize_network_address(data)
        msg['from_addr'] = deserialize_network_address(data)
        msg['nonce'] = unpack("<Q", data.read(8))
        msg['user_agent'] = deserialize_string(data)
        msg['height'] = unpack("<i", data.read(4))
        try:
            msg['relay'] = struct.unpack("<?", data.read(1))[0]
        except struct.error:
            msg['relay'] = False

        return msg

def deserialize_header(data):
        msg = {}
        data = StringIO(data)

        msg['magic_number'] = data.read(4)
        if msg['magic_number'] != MAGIC_NUMBER:
            raise ValueError("{} != {}".format(
                hexlify(msg['magic_number']), hexlify(MAGIC_NUMBER)))

        msg['command'] = data.read(12).strip("\x00")
        msg['length'] = struct.unpack("<I", data.read(4))[0]
        msg['checksum'] = data.read(4)

        return msg


def deserialize_ping_payload(data):
        data = StringIO(data)
        nonce = unpack("<Q", data.read(8))
        msg = {
            'nonce': nonce,
        }
        return msg

def deserialize_addr_payload(data):
        msg = {}
        data = StringIO(data)

        msg['count'] = deserialize_int(data)
        msg['addr_list'] = []
        for _ in xrange(msg['count']):
            network_address = deserialize_network_address(
                data, has_timestamp=True)
            msg['addr_list'].append(network_address)

        return msg

    
def deserialize_msg(data):
        msg = {}
        data_len = len(data)
        if data_len < HEADER_LEN:
            raise ValueError("got {} of {} bytes".format(data_len, HEADER_LEN))

        data = StringIO(data)
        header = data.read(HEADER_LEN)
        msg.update(deserialize_header(header))

        if (data_len - HEADER_LEN) < msg['length']:
            required_len = HEADER_LEN + msg['length']
            raise PayloadTooShortError("got {} of {} bytes".format(data_len, HEADER_LEN + msg['length']))

        payload = data.read(msg['length'])
        computed_checksum = sha256(sha256(payload))[:4]
        if computed_checksum != msg['checksum']:
            raise ValueError("{} != {}".format(hexlify(computed_checksum), hexlify(msg['checksum'])))

        if msg['command'] == "version":
            msg.update(deserialize_version_payload(payload))
        elif msg['command'] == "ping" or msg['command'] == "pong":
            msg.update(deserialize_ping_payload(payload))
        elif msg['command'] == "addr":
            msg.update(deserialize_addr_payload(payload))
        return (msg, data.read())


def create_connection(address, timeout=30, source_address=None,
                      proxy=None):
    if address[0].endswith(".onion") and proxy is None:
        raise ValueError("tor proxy is required to connect to .onion address")
    if proxy:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy[0], proxy[1])
        sock = socks.socksocket()
        sock.settimeout(timeout)
        try:
            sock.connect(address)
        except socks.ProxyError as err:
            raise ValueError(err)
        return sock
    if ":" in address[0] and source_address and ":" not in source_address[0]:
        source_address = None
    return socket.create_connection(address, timeout=timeout, source_address=source_address)


class Connection(object):
    def __init__(self, to_addr, from_addr=("0.0.0.0", 0), **conf):
        self.to_addr = to_addr
        self.from_addr = from_addr
        self.socket_timeout = 10
        self.proxy = None #('127.0.0.1', 1080)
        self.socket = None

    def open(self):
        self.socket = create_connection(
                self.to_addr, timeout=self.socket_timeout, source_address=self.from_addr, proxy=self.proxy)

    def close(self):
        if self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except socket.error:
                pass
            finally:
                self.socket.close()

    def send(self, data):
        #print('send', data)
        self.socket.sendall(data)

    def recv(self, length=0):
        start_t = time.time()
        if length > 0:
            chunks = []
            while length > 0:
                chunk = self.socket.recv(SOCKET_BUFSIZE)
                if not chunk:
                    raise ValueError(
                        "{} closed connection".format(self.to_addr))
                chunks.append(chunk)
                length -= len(chunk)
            data = ''.join(chunks)
        else:
            data = self.socket.recv(SOCKET_BUFSIZE)
            if not data:
                raise ValueError("{} closed connection".format(self.to_addr))
        if len(data) > SOCKET_BUFSIZE:
            end_t = time.time()
            self.bps.append((len(data) * 8) / (end_t - start_t))
        return data

    def get_messages(self, length=0, commands=None):
        msgs = []
        data = self.recv(length=length)
        #print('get_messages ' + commands[0] + ', want ' + str(length) + ' get ' + str(len(data)))
        while len(data) > 0:
            try:
                (msg, data) = deserialize_msg(data)
            except PayloadTooShortError:
                print 'PayloadTooShortError'
                data += self.recv(
                    length=self.serializer.required_len - len(data))
                (msg, data) = self.serializer.deserialize_msg(data)
            if msg.get('command') == "ping":
                self.pong(msg['nonce'])  # respond to ping immediately
            elif msg.get('command') == "version":
                self.verack()  # respond to version immediately
            msgs.append(msg)
        #print('get_messages', msgs)
        if len(msgs) > 0 and commands:
            msgs[:] = [m for m in msgs if m.get('command') in commands]
        return msgs


    def pong(self, nonce):
        # [pong] >>>
        msg = serialize_msg(command="pong", nonce=nonce)
        self.send(msg)


    def verack(self):
        # [verack] >>>
        msg = serialize_msg(command="verack")
        self.send(msg)


    def getaddr(self, block=True):
        msg = serialize_msg(command="getaddr")
        self.send(msg)

        if not block:
            return None
        time.sleep(5)
        msgs = self.get_messages(commands=["addr"])
        return msgs

    def handshake(self):
        msg = serialize_msg(command="version", to_addr=self.to_addr, from_addr=self.from_addr)
        self.send(msg)

        # <<< [version 124 bytes] [verack 24 bytes]
        time.sleep(3)
        msgs = self.get_messages(length=148, commands=["version", "verack"])
        
        if len(msgs) > 0:
            msgs[:] = sorted(msgs, key=itemgetter('command'), reverse=True)
        return msgs

    
if __name__ == '__main__':
    port = 9333
    host = '120.79.161.218'
    host = '101.132.70.217'
    host = '159.138.28.122'
    to_addr = (host, port)
    to_services = 1  # NODE_NETWORK
    conn = Connection(to_addr, to_services=to_services)

    print("open")
    conn.open()

    print("handshake")
    handshake_msgs = conn.handshake()
    version_msg = None
    for item in handshake_msgs:
        if 'version' == item['command']:
            version_msg = item
            break
    print version_msg['height']
    services = version_msg['services']
    if services == 13:
        services = 'NODE_NETWORK NODE_BLOOM NODE_XTHIN'
    else:
        services = str(services) + 'todo'
    print version_msg['user_agent'] + '|' + str(version_msg['version']) + '|' + services
    
    print("getaddr")
    addr_msgs = conn.getaddr()
    print addr_msgs
    for item in addr_msgs[0]['addr_list']:
        print item['ipv4'] + ':' + str(item['port'])
