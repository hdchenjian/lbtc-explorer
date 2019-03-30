#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, get_node_by_ip, \
    add_not_valid_node, add_many_tx, add_one_tx, update_one_tx, find_one_tx, find_many_tx
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
config.from_object(config_online)

@singleton('/tmp/parse_lbtc_block.pid')
def parse_lbtc_block():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        best_block_hash = rpc_connection.getbestblockhash()
        best_block = rpc_connection.getblock(best_block_hash)
        best_height = best_block['height']
        #best_height = 10
        current_height = 5126
        while current_height <= best_height:
            current_block_hash = rpc_connection.getblockhash(current_height)
            current_block_info = rpc_connection.getblock(current_block_hash)
            vin_tx_id = []
            tx_id_to_tx_info = {}
            tx_mongos = []
            for _tx_id in current_block_info['tx']:
                tx_info = rpc_connection.gettransactionnew(_tx_id)
                tx_mongo = {'_id': _tx_id,
                            'time': datetime.datetime.fromtimestamp(current_block_info['time']),
                            'size': tx_info['vsize'],
                            'input': [],
                            'output': []}
                #print(tx_info)
                tx_id_to_tx_info[_tx_id] = tx_info
                for _vin in tx_info['vin']:
                    if 'coinbase' in _vin:
                        pass
                    else:
                        vin_tx_id.append(_vin['txid'])
                vout_index = 0
                for _vout in tx_info['vout']:
                    if _vout['n'] != vout_index: raise(ValueError('vout index error'))
                    if _vout['scriptPubKey']['type'] == 'pubkeyhash' or _vout['scriptPubKey']['type'] == 'scripthash':
                        if len(_vout['scriptPubKey']['addresses']) != 1:
                            raise ValueError('vout multi addresses')
                        tx_mongo['output'] += [_vout['n'], _vout['scriptPubKey']['addresses'][0], str(_vout['value'])]
                    elif _vout['scriptPubKey']['type'] == 'nulldata':
                        tx_mongo['output'] += [_vout['n'], 'nulldata', str(_vout['value'])]
                    else:
                        raise(ValueError('vout type unknow'))
                    vout_index += 1
                #print(tx_mongo)
                #tx_mongo['output'].sort(key=lambda x: x[0])
                tx_mongos.append(tx_mongo)
            old_mongo_tx_info_map = {}
            if vin_tx_id:
                old_mongo_tx_info = find_many_tx(vin_tx_id)
                for item in old_mongo_tx_info:
                    old_mongo_tx_info_map[item['_id']] = item
                for item in tx_mongos:
                    old_mongo_tx_info_map[item['_id']] = item
            for _tx_info in tx_mongos:
                tx_info = tx_id_to_tx_info[_tx_info['_id']]
                for _vin in tx_info['vin']:
                    if 'coinbase' in _vin:
                        _tx_info['input'] += ['coinbase', '']
                    else:
                        _tx_info['input'] += [old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 1],
                                              old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 2]]
                    
            #print(current_block_info)
            add_many_tx(tx_mongos)
            print('current_height ', current_height, tx_mongos)
            current_height += 1
            #exit()
    except Exception as e:
        print(e)
        raise
        
    

if __name__ == '__main__':
    parse_lbtc_block()
