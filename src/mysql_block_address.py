#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
from decimal import Decimal

from v8.config import config, config_online
from v8.engine.handlers.node_handler import find_many_tx, update_block_status, \
    get_block_status, add_block_info, update_many_address_info
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decorators import singleton
config.from_object(config_online)

from config import PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT

@singleton('/tmp/mysql_block_address.pid')
def mysql_block_address():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)
        
        best_block_hash = rpc_connection.getbestblockhash()
        best_block = rpc_connection.getblock(best_block_hash)
        best_height = best_block['height']
        best_height = 4765484
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
            current_block_info['tx_num'] = len(current_block_info['tx'])
            add_block_info_result = add_block_info(current_block_info)
            if not add_block_info_result:
                print('add_block_info failed, current_height ', current_height)
                break

            current_tx_ids = []
            for _tx_id in current_block_info['tx']:
                current_tx_ids.append(_tx_id)
            mongo_tx_info = find_many_tx(current_tx_ids)
            need_update = []
            for item in mongo_tx_info:
                for i in range(0, len(item['input']) // 2):
                    if item['input'][2*i] == 'coinbase': continue
                    need_update.append({'address': item['input'][2*i],
                                        'amount': 0 - Decimal(item['input'][2*i + 1]),
                                        'time': item['time'],
                                        'height': current_height,
                                        'hash': item['_id']})
                for i in range(0, len(item['output']) // 3):
                    if item['output'][3*i + 1] == 'nulldata': continue
                    need_update.append({'address': item['output'][3*i + 1],
                                        'amount': item['output'][3*i + 2],
                                        'time': item['time'],
                                        'height': current_height,
                                        'hash': item['_id']})
            update_many_address_info(need_update)
            #print(need_update)
            print('current_height', current_height)
            current_height += 1
        update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, {'height': current_height})
    except Exception as e:
        print(e)
        raise
        
    

if __name__ == '__main__':
    mysql_block_address()
