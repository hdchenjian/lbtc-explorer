#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time
from decimal import Decimal

import multiprocessing

from v8.config import config, config_online
from v8.engine.handlers.node_handler import find_many_tx, update_block_status, \
    get_block_status, add_block_info, update_many_address_info, add_many_tx, \
    update_all_delegate, update_all_committee, update_all_proposal, \
    update_most_rich_address, update_network_tx_statistics, update_address_growth_daily_info, \
    update_transaction_daily_info, delete_many_tx, delete_block_info, query_all_delegate
from bitcoinrpc.authproxy import AuthServiceProxy

from decorators import singleton
from config import PARSE_BLOCK_STATUS_KYE_MYSQL_VALID_TX_HEIGHT

config.from_object(config_online)


@singleton('/tmp/valid_tx.pid')
def valid_tx():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        best_block_hash = rpc_connection.getbestblockhash()
        best_block = rpc_connection.getblock(best_block_hash)
        best_height = best_block['height'] - 1000
        # best_height = 5827263 + 100
        
        block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_VALID_TX_HEIGHT)
        if not block_status:
            block_status = {'height': 5827263}
        current_height = block_status['height']
        print('start from height ', current_height, 'best_height: ', best_height)
        next_block_hash = ''
        tx_hash = []
        while current_height <= best_height:
            current_delegate_list = []
            if not next_block_hash:
                next_block_hash = rpc_connection.getblockhash(current_height)
            current_block_info = rpc_connection.getblock(next_block_hash)
            if not current_block_info:
                break

            tx_hash += current_block_info['tx']

            if current_height % 50000 == 0:
                print('current_height ', current_height)
            current_height += 1
            if 'nextblockhash' not in current_block_info:
                break
            next_block_hash = current_block_info['nextblockhash']

        txs = find_many_tx(tx_hash)
        if len(txs) != len(tx_hash):
            print('blockchain rollback!\n', 'start from height ', block_status['height'], 'best_height: ', best_height)
        else:
            update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_VALID_TX_HEIGHT, {'height': current_height})

    except Exception as e:
        print(e)
        raise



if __name__ == '__main__':
    valid_tx()
