#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Resolves hostname and GeoIP data for each reachable node. """

import geoip2.database
from geoip2.errors import AddressNotFoundError
# from decimal import Decimal
import threading
import time
import datetime
import socket

from decorators import singleton
from connection import Connection

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, delete_node, \
    add_not_valid_node_connect_try_times, \
    delete_not_valid_node, update_node_distribution, update_block_status, \
    get_node_by_ip

from config import REST_BLOCK_STATUS_KYE_NODE_IP_TYPE
config.from_object(config_online)

# MaxMind databases
GEOIP_CITY = geoip2.database.Reader("geoip/GeoLite2-City.mmdb")
GEOIP_COUNTRY = geoip2.database.Reader("geoip/GeoLite2-Country.mmdb")
ASN = geoip2.database.Reader("geoip/GeoLite2-ASN.mmdb")


def resolve_address(address):
    try:
        gcity = GEOIP_CITY.city(address)
        '''
        prec = Decimal('.000001')
        if gcity.location.latitude is not None and gcity.location.longitude is not None:
            lat = float(Decimal(gcity.location.latitude).quantize(prec))
            lng = float(Decimal(gcity.location.longitude).quantize(prec))
        '''
        timezone = gcity.location.time_zone
        # gcountry = GEOIP_COUNTRY.country(address)

        if address.endswith(".onion"):
            asn = "TOR"
            org = "Tor network"
        else:
            asn_record = ASN.asn(address)
            asn = 'AS{}'.format(asn_record.autonomous_system_number)
            org = asn_record.autonomous_system_organization
        city_name = gcity.city.name
        if city_name is None:
            city_name = gcity.country.names['en']
        else:
            city_name = city_name + ', ' + gcity.country.names['en']
        if not city_name:
            city_name = ''
        if not timezone:
            timezone = ''
        if not org:
            org = ''
        return (city_name, timezone, org, asn)

    except AddressNotFoundError:
        return None


def find_node(node, max_height, ip_to_node):
    host, port = node['ip'].split(':')
    to_addr = (host, int(port))
    to_services = 1  # NODE_NETWORK
    conn = Connection(to_addr, to_services=to_services)
    try:
        conn.open()
        handshake_msgs = conn.handshake()
        version_msg = None
        for item in handshake_msgs:
            if 'version' == item['command']:
                version_msg = item
                break

        height = version_msg['height']
        services = version_msg['services']
        node_info = {}
        if services == 13:
            node_info['services'] = 'NODE_NETWORK NODE_BLOOM NODE_XTHIN'
        elif services == 1:
            node_info['services'] = 'NODE_NETWORK'
        else:
            node_info['services'] = str(services) + 'todo'
        node_info['user_agent'] = \
            version_msg['user_agent'] + ' (' + str(version_msg['version']) + ')'
        node_info['services'] = \
            node_info['services'] + '(' + str(version_msg['services']) + ')'
        node_info['height'] = height
        if (not node['status']):
            resolve_result = resolve_address(node['ip'].split(':')[0])
            if resolve_result:
                node_info['location'] = resolve_result[0]
                node_info['timezone'] = resolve_result[1]
                node_info['network'] = resolve_result[2]
                node_info['asn'] = resolve_result[3]
                node_info['status'] = 1
        update_or_add_node(node['ip'], node_info)
        delete_not_valid_node(node['ip'])

        addr_msgs = conn.getaddr()
        if len(addr_msgs) > 1:
            print('get new node list', addr_msgs)
        else:
            pass
    except (socket.timeout, socket.error,  OSError, ValueError) as e:
        exception_str = str(e)
        if 'timed out' not in exception_str and 'Connection refused' not in exception_str and \
           'No route to host' not in exception_str and 'closed connection' not in exception_str \
           and 'Network is unreachable' not in exception_str:
            print(node['ip'], e)
        if node['height'] != -1:
            if (datetime.datetime.now() -
                datetime.datetime.strptime(node['create_time'], '%Y-%m-%dT%H:%M:%S')) \
                    .total_seconds > 3600:
                if max_height - node['height'] > 24 * 3600 or \
                   (max_height - node['height'] > 8 * 3600 and not node['ip'].endswith(':9333')):
                    # print(node['ip'], 'long time offline, delete it')
                    delete_node(node['ip'])
                    # pass
        else:
            if node['count'] > 100:
                delete_not_valid_node(node['ip'])
            else:
                add_not_valid_node_connect_try_times(node['ip'])
        return
    for response in addr_msgs:
        for item in response['addr_list']:
            if item['ipv4']:
                ip = item['ipv4'] + ':' + str(item['port'])
            elif item['ipv6']:
                ip = item['ipv6'] + ':' + str(item['port'])
                print('get ipv6: ', item, '\n\n')
            elif item['onion']:
                ip = item['onion']
                print('get onion: ', item, '\n\n')
            else:
                print('error: ip is empty: ', item)
                continue
            if ip == node['ip']:
                continue
            if ip in ip_to_node:
                continue
            # add_not_valid_node(ip)

            node_info = {}
            if item['services'] == 13:
                node_info['services'] = 'NODE_NETWORK NODE_BLOOM NODE_XTHIN'
            elif item['services'] == 1:
                node_info['services'] = 'NODE_NETWORK'
            else:
                node_info['services'] = str(services) + 'todo'
            node_info['services'] = \
                node_info['services'] + '(' + str(version_msg['services']) + ')'
            node_info['user_agent'] = '(not connected)'
            node_by_ip = get_node_by_ip(ip)
            if not node_by_ip or not node_by_ip['status']:
                resolve_result = resolve_address(node['ip'].split(':')[0])
                if resolve_result:
                    node_info['location'] = resolve_result[0]
                    node_info['timezone'] = resolve_result[1]
                    node_info['network'] = resolve_result[2]
                    node_info['asn'] = resolve_result[3]
                    node_info['status'] = 1
            update_or_add_node(ip, node_info)


def get_node_NodeDistribution():
    all_node = get_all_node(2)
    country_map = {}
    country_info = {}
    ip_type = {'node_num': len(all_node),
               'node_connected': 0,
               'node_not_connected': 0,
               'ipv4': 0,
               'ipv6': 0,
               'onion': 0}
    for _node in all_node:
        if _node['ip'].endswith(".onion"):
            ip_type['onion'] += 1
        elif len(_node['ip'].split(':')) > 2:
            ip_type['ipv6'] += 1
        else:
            ip_type['ipv4'] += 1
        if '(not connected' not in _node['user_agent']:
            ip_type['node_connected'] += 1
        else:
            ip_type['node_not_connected'] += 1

        country = _node['location']
        if ', ' in country:
            city_name, country = country.split(', ')
        if country not in country_map:
            country_map[country] = 1
        else:
            country_map[country] += 1
    update_block_status(REST_BLOCK_STATUS_KYE_NODE_IP_TYPE, ip_type)
    total_node = 0
    for country in country_map:
        total_node += country_map[country]
    if total_node == 0:
        return
    country_map_list = []
    for country in country_map:
        country_map_list.append((country, country_map[country]))
    country_map_list.sort(key=lambda x: x[1], reverse=True)
    rank = 1
    for country in country_map_list:
        info = {}
        info['rank'] = rank
        info['node_num'] = country[1]
        info['node_persent'] = float(country[1]) / total_node * 100
        rank += 1
        country_info[country[0]] = info
    # print country_info
    if country_info:
        update_node_distribution(country_info)


@singleton('/tmp/crawl_all_node.pid')
def crawl_all_node():

    all_node = get_all_node(2)
    tasks = []
    max_height = None
    if all_node:
        max_height = all_node[0]['height']
    ip_to_node = {}
    for _node in all_node:
        ip_to_node[_node['ip']] = _node

    for _node in all_node:
        # print('start', _node['ip'])
        t = threading.Thread(target=find_node, args=(_node, max_height, ip_to_node))
        t.start()
        tasks.append(t)
        time.sleep(0.05)
    for t in tasks:
        t.join()
    get_node_NodeDistribution()

    '''
    tasks_not_valid = []
    all_not_valid_node = get_all_not_valid_node()
    for _node in all_not_valid_node:
        # print('start', _node['ip'])
        _node['height'] = -1
        _node['status'] = 0
        t = threading.Thread(target=find_node, args=(_node, max_height, ip_to_node))
        t.start()
        tasks_not_valid.append(t)
        time.sleep(0.05)
    for t in tasks_not_valid:
        t.join()
    '''


if __name__ == '__main__':
    crawl_all_node()
