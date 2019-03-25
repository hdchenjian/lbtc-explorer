#!/usr/bin/env python
# encoding: utf-8

#curl --user luyao:123456  --data-binary '{"jsonrpc":"1.0","id":"curltest","method": "getinfo","params":[]}' -H 'content-type:text/plain;' http://127.0.0.1:8332/

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, add_or_update_node, update_node

config.from_object(config_online)

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
import pprint

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
try:
    #print(rpc_connection.help())
    #print(rpc_connection.getmemoryinfo())
    print(rpc_connection.getinfo())
    #print(rpc_connection.getmempoolinfo())
    #print(rpc_connection.getrawmempool())
    '''
    delegates = rpc_connection.listdelegates()
    pprint.pprint(delegates)
    print len(delegates)
    '''
    delegateName = 'zmz'
    #print(rpc_connection.getdelegatefunds(delegateName))
    #print(rpc_connection.getdelegatevotes(delegateName))

    
    #print(rpc_connection.getmininginfo())
    #print(rpc_connection.getnetworkinfo())
    peerinfo = rpc_connection.getpeerinfo()
    print peerinfo[0]
    print(len(peerinfo))
    for _peer in peerinfo:
        ip = _peer['addr']
        user_agent = _peer['subver']
        services = _peer['services']
        if services == 13:
            services = 'NODE_NETWORK NODE_BLOOM NODE_XTHIN'
        else:
            services = str(services) + 'todo'
        location = 'China'
        network = 'Hangzhou Alibaba Advertising Co.,Ltd.:AS37963'
        height = 4608395
        pix = 0.5
        status = 1
        try:
            add_or_update_node(ip, user_agent, location, network, height, pix, status)
        except Exception as e:
            print(e)
    #print(rpc_connection.getnettotals())
    
    #pprint.pprint(rpc_connection.getinfo())
    #pprint.pprint(rpc_connection.getblockchaininfo())
    #pprint.pprint(rpc_connection.getnewaddress("account1"))
    #print(rpc_connection.getaddressesbylabel("account1"))  # 1BcNXePEwhJHDrvmC6xBszrzDsrcJ6wope
    #pprint.pprint(rpc_connection.getbalance())
    #pprint.pprint(rpc_connection.setgenerate(True))
except Exception as e:
    print unicode(e)
#print(rpc_connection.getaccount('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.getaccountaddress("account1"))  # 1JVjemAg9FrNhesrJmEq1HVnEh7WxMtZHy
#print(rpc_connection.getaddressesbyaccount("account1")) #[u'1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C', u'1JVjemAg9FrNhesrJmEq1HVnEh7WxMtZHy']
#print(rpc_connection.getblockcount())
#print(rpc_connection.getblocknumber())
#print(rpc_connection.getgenerate())
#print(rpc_connection.gethashespersec())
#print(rpc_connection.getreceivedbyaccount('account1'))
#print(rpc_connection.getreceivedbyaddress('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.validateaddress('1ZJaSNGw37MPYejr9uWzx9ZLyhvFt9b2C'))
#print(rpc_connection.getwork())
#print(rpc_connection.getbalance('*'))
#print(rpc_connection.listtransactions("account1"))
#print(rpc_connection.listaccounts())
#print rpc_connection.listreceivedbyaddress(6)
#print rpc_connection.sendtoaddress("11yEmxiMso2RsFVfBcCa616npBvGgxiBX", 10)
