#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import random
from decimal import Decimal

from v8.config import config, config_online
from v8.engine.handlers.node_handler import find_many_tx, update_block_status, \
    get_block_status, add_block_info, update_many_address_info, add_many_tx, \
    update_one_delegate, update_many_delegate_active
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
config.from_object(config_online)


from config import PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))

def parse_lbtc_block_main():
    try:
        coinbase_address = []
        best_block_hash = rpc_connection.getbestblockhash()
        best_block = rpc_connection.getblock(best_block_hash)
        best_height = best_block['height']
        block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)
        if not block_status:
            block_status = {"height": 1}
            update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, block_status)
        current_height = block_status['height']
        print('start from height ', current_height)
        next_block_hash = ''
        while current_height <= best_height:
            if not next_block_hash:
                next_block_hash = rpc_connection.getblockhash(current_height)
            current_block_info = rpc_connection.getblock(next_block_hash)
            #print(current_block_info)
            if not current_block_info:
                break
            next_block_hash = current_block_info['nextblockhash']
            
            vin_tx_id = []
            tx_id_to_raw_tx_info = {}
            tx_mongos = []
            for _tx_id in current_block_info['tx']:
                tx_info = rpc_connection.gettransactionnew(_tx_id)
                tx_mongo = {'_id': _tx_id,
                            'time': datetime.datetime.fromtimestamp(current_block_info['time']),
                            'size': tx_info['vsize'],
                            'height': current_height,
                            'input': [],
                            'output': []}
                #print(tx_info)
                tx_id_to_raw_tx_info[_tx_id] = tx_info
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
            for _tx_info_mongo in tx_mongos:
                tx_info = tx_id_to_raw_tx_info[_tx_info_mongo['_id']]
                for _vin in tx_info['vin']:
                    if 'coinbase' in _vin:
                        _tx_info_mongo['input'] += ['coinbase', '']
                    else:
                        _tx_info_mongo['input'] += [old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 1],
                                              old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 2]]
                    
            #print(current_block_info)
            add_many_tx(tx_mongos)

            current_block_info['tx_num'] = len(current_block_info['tx'])
            add_block_info_result = add_block_info(current_block_info)
            if not add_block_info_result:
                print('add_block_info failed, current_height ', current_height)
                break

            need_update = []
            for item in tx_mongos:
                for i in range(0, len(item['input']) // 2):
                    if item['input'][2*i] == 'coinbase': continue
                    need_update.append({'address': item['input'][2*i],
                                        'amount': 0 - Decimal(item['input'][2*i + 1]),
                                        'time': item['time'],
                                        'hash': item['_id']})
                for i in range(0, len(item['output']) // 3):
                    if item['output'][3*i + 1] == 'nulldata': continue
                    need_update.append({'address': item['output'][3*i + 1],
                                        'amount': item['output'][3*i + 2],
                                        'time': item['time'],
                                        'hash': item['_id']})
            tx_time = datetime.datetime.fromtimestamp(current_block_info['time'])
            need_update_merge = {}
            if len(need_update) > 1:
                for item in need_update:
                    if item['hash'] not in need_update_merge:
                        need_update_merge[item['hash']] = {item['address']: Decimal(item['amount'])}
                    else:
                        if item['address'] not in need_update_merge[item['hash']]:
                            need_update_merge[item['hash']][item['address']] = Decimal(item['amount'])
                        else:
                            need_update_merge[item['hash']][item['address']] += Decimal(item['amount'])
            if need_update_merge:
                need_update = []
                for _hash in need_update_merge:
                    for _address in need_update_merge[_hash]:
                        need_update.append({'address': _address,
                                            'amount': need_update_merge[_hash][_address],
                                            'time':tx_time,
                                            'hash': _hash
                                            })
            update_many_address_info(need_update)

            print('current_height ', current_height)
            current_height += 1
            #exit()

            for item in tx_mongos:
                for i in range(0, len(item['input']) // 2):
                    if item['input'][2*i] == 'coinbase':
                        pass
                        #coinbase_address.append(item['output'][1])
        update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, {'height': current_height})
        #update_many_delegate_active(coinbase_address)
    except Exception as e:
        print(e)
        raise
        

def query_all_delegate():
    all_delegate = rpc_connection.listdelegates()
    for _delegate in all_delegate:
        _delegate['_id'] = _delegate['address']
        _delegate.pop('address')
        _delegate['funds'] = str(Decimal(rpc_connection.getdelegatefunds(_delegate['name'])) / 100000000)
        _delegate['votes'] = str(Decimal(rpc_connection.getdelegatevotes(_delegate['name'])) / 100000000)
        _delegate['votes_address'] = rpc_connection.listreceivedvotes(_delegate['name'])
        update_one_delegate(_delegate)


@singleton('/tmp/parse_lbtc_block.pid')
def parse_lbtc_block():
    while(True):
        parse_lbtc_block_main()
        break
        if random.random() > 0.1:
            query_all_delegate()
        time.sleep(2)


if __name__ == '__main__':
    parse_lbtc_block()
