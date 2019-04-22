#!/usr/bin/env python3
# encoding: utf-8

from v8.config import config, config_online
# from v8.engine.handlers.node_handler import update_all_committee, update_all_proposal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
config.from_object(config_online)


@singleton('/tmp/update_rpc_node.pid')
def update_rpc_node():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        print(rpc_connection.getblock('8c45c1b3ef9821a481acff0a932d081867bc65dd111'))
    except JSONRPCException:
        pass
    try:
        # print(rpc_connection.help())
        # best_block_hash = rpc_connection.getbestblockhash()
        # blockhash = rpc_connection.getblockhash(2050113)
        # print(blockhash)
        # best_block = rpc_connection.getblock(best_block_hash)
        # print(best_block_hash, best_block)
        # tx_id = '163d33738e9f2fc4b3cdb860fe8fe3d16fcae6a9d3a8c805e8c8b6607fe14c53'
        # print(rpc_connection.gettxout(tx_id, 0))

        # print(rpc_connection.gettxoutproof([tx_id]))
        print(rpc_connection.gettxoutsetinfo())

        # print(rpc_connection.gettransactionnew('45581dcfe9324bdee8bfed7a3cd20000839cfd836792fb116d9c2bfe187df67f'))

        # print(rpc_connection.getchaintips())
        # print(rpc_connection.getmempoolinfo())
        # print(rpc_connection.getrawmempool(True))

        # print(rpc_connection.listreceivedvotes('TestDelegates'))
        # print(rpc_connection.listvotercommittees('1CKbTd4ThjmRFhaGbGVfqa5B1ivLuxYHQD'))
        # print(rpc_connection.listcommitteevoters('TestCommitteesName'))
        # print(rpc_connection.listvoteddelegates('1LAMDkarMYfZXcRQX5ZKhSafQBJqcRf91v'))

        # print(rpc_connection.listcommitteebills('TestCommitteesName'))
        # print(rpc_connection.listvoterbills('1CKbTd4ThjmRFhaGbGVfqa5B1ivLuxYHQD'))

        '''
        print(rpc_connection.getmininginfo())
        print(rpc_connection.getblocktemplate())
        print(rpc_connection.getnetworkhashps(5031939))
        '''
    except Exception as e:
        print(e)
        raise


if __name__ == '__main__':
    update_rpc_node()
