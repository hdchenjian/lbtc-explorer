#!/usr/bin/env python
# encoding: utf-8

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, get_node_by_ip
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
from crawl import resolve_address
config.from_object(config_online)

@singleton('/tmp/update_rpc_node.pid')
def update_rpc_node():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        #print(rpc_connection.help())
        peerinfo = rpc_connection.getpeerinfo()
        #print(len(peerinfo))
        for _peer in peerinfo:
            ip = _peer['addr']
            user_agent = _peer['subver'] + ' (' + str(_peer['version']) + ')'
            services = _peer['services']
            if services == '000000000000000d':
                services = 'NODE_NETWORK NODE_BLOOM NODE_XTHIN (13)'
            else:
                services = str(services) + 'todo'
            user_agent = user_agent + '|' + services
            height = _peer['synced_blocks']
            node_info = {'user_agent': user_agent,
                         'height': height}
            node_by_ip = get_node_by_ip(ip)
            #print node_by_ip
            if (not node_by_ip or (not node_by_ip['location'] or not node_by_ip['network'])):
                resolve_result = resolve_address(ip.split(':')[0])
                if resolve_result:
                    node_info['location'] = resolve_result[0]
                    node_info['network'] = resolve_result[1]
            #print node_info
            update_or_add_node(ip, node_info)
    except Exception as e:
        print unicode(e)
    

if __name__ == '__main__':
    update_rpc_node()
