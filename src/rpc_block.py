#!/usr/bin/env python3
# encoding: utf-8

from decimal import Decimal
import datetime

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, get_node_by_ip, \
    add_not_valid_node, update_all_committee, update_all_proposal
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
        blockhash = rpc_connection.getblockhash(2050113)
        #print(blockhash)
        best_block = rpc_connection.getblock(blockhash)
        #print best_block
        #print(rpc_connection.gettxout('8c7ee1999644b81200390a182a0b9e4f85574991cddb7b7235538f02b79d2c26', 0)) # 1 block
        #print(rpc_connection.gettxout('8049a32c02489a763fdfd4e2e328c43e8361d5ac1d210f03d070ca3a0de5ac0f', 0)) # 2 block
        #print(rpc_connection.gettxout('dfd25db563092a8f08a11dd9843ed715b305d8e83aa9d78c7cff91ec279c5a27', 1)) # 3 block

        #print(rpc_connection.gettxout('5db9dd92e738ed8a07a52d52a9907988b1b19d1354e160e0c11bd9ac0c5e058e', 0)) # multi input multi output
        #print(rpc_connection.gettxout('163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53', 1))

        #print(rpc_connection.gettxout('163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53', 0)) # vote

        #print(rpc_connection.gettxoutproof(['8049a32c02489a763fdfd4e2e328c43e8361d5ac1d210f03d070ca3a0de5ac0f']))
        #print(rpc_connection.gettxoutproof(['5db9dd92e738ed8a07a52d52a9907988b1b19d1354e160e0c11bd9ac0c5e058e']))
        #print(rpc_connection.gettxoutsetinfo())

        #print(rpc_connection.gettransactionnew('5db9dd92e738ed8a07a52d52a9907988b1b19d1354e160e0c11bd9ac0c5e058e'))
        #print(rpc_connection.gettransactionnew('65369628bbd137801aceba9859c55851a13bc931ccd8426f933f7dc3122b002f'))
        
        #print(rpc_connection.gettransactionnew('b4ad2efca6144cac8de5edf23174facbee2b7b1de5b895753eba7d59d709f886'))
            
        #print(rpc_connection.getchaintips())
        #print(rpc_connection.getmempoolinfo())
        #print(rpc_connection.getrawmempool(True))

        #print(rpc_connection.listreceivedvotes('TestDelegates'))
        #print(rpc_connection.listvotercommittees('1CKbTd4ThjmRFhaGbGVfqa5B1ivLuxYHQD'))
        #print(rpc_connection.listcommitteevoters('TestCommitteesName'))
        #print(rpc_connection.listvoteddelegates('1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v'))

        print(rpc_connection.listcommitteebills('TestCommitteesName'))
        print(rpc_connection.listvoterbills('1CKbTd4ThjmRFhaGbGVfqa5B1ivLuxYHQD'))
    except Exception as e:
        print(e)
        raise
    

if __name__ == '__main__':
    update_rpc_node()
