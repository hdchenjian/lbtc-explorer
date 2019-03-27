#!/usr/bin/env python
# encoding: utf-8

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, get_node_by_ip, \
    add_not_valid_node
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
from crawl import resolve_address
config.from_object(config_online)

@singleton('/tmp/update_rpc_node.pid')
def update_rpc_node():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        #print(rpc_connection.help())
        best_block_hash = rpc_connection.getbestblockhash()
        blockhash = rpc_connection.getblockhash(1)
        best_block = rpc_connection.getblock(best_block_hash)
        #print best_block
        #print(rpc_connection.gettxinfo('8c7ee1999644b81200390a182a0b9e4f85574991cddb7b7235538f02b79d2c26'))
        #print(rpc_connection.getchaintips())
        print(rpc_connection.getmempoolinfo())
        #print(rpc_connection.getrawmempool(True))
    except Exception as e:
        print unicode(e)
    

if __name__ == '__main__':
    update_rpc_node()
