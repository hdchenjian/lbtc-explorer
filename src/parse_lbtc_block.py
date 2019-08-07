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
from config import PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, \
    REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME, REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO, \
    REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST, REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME, \
    REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS, \
    REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS, REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS, \
    REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE

config.from_object(config_online)


def parse_lbtc_delegate():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)
        best_height = block_status['height'] - 1
        #best_height = 7006 + 3
        current_height = 7005
        print('start from height ', current_height, 'best_height: ', best_height)
        next_block_hash = ''
        address_to_delegate_info = {}
        for _delegate_info in query_all_delegate():
            address_to_delegate_info[_delegate_info['_id']] = _delegate_info
        current_delegate_address = None
        current_index = 0
        delegate_rate = {}
        current_delegate = []
        while current_height <= best_height:
            current_delegate_list = []
            if not next_block_hash:
                next_block_hash = rpc_connection.getblockhash(current_height)
            current_block_info = rpc_connection.getblock(next_block_hash)
            if not current_block_info:
                break

            _tx_id = current_block_info['tx'][0]
            tx_info = rpc_connection.gettransactionnew(_tx_id)
            if 'coinbase' in tx_info['vin'][0]:
                for _vout in tx_info['vout']:
                    if 'delegates' in _vout:
                        current_delegate = []
                        for _delegate in _vout['delegates']:
                            if _delegate in address_to_delegate_info:
                                current_delegate_list.append(_delegate)
                                current_delegate.append(_delegate)
                                if _delegate not in delegate_rate:
                                    delegate_rate[_delegate] = {'block_vote': 1, 'block_product': 0}
                                else:
                                    delegate_rate[_delegate]['block_vote'] += 1
                        #print('current_delegate', current_delegate, len(current_delegate))
                        #print(len(current_delegate))
                if tx_info['vout'][0]['scriptPubKey']['type'] == 'pubkeyhash' or \
                   tx_info['vout'][0]['scriptPubKey']['type'] == 'scripthash':
                    if len(tx_info['vout'][0]['scriptPubKey']['addresses']) != 1:
                        raise ValueError('vout multi addresses')
                    current_delegate_address = tx_info['vout'][0]['scriptPubKey']['addresses'][0]
                    if current_delegate_address in delegate_rate:
                        delegate_rate[current_delegate_address]['block_product'] += 1
                        current_index = current_delegate.index(current_delegate_address)
                        if current_index == 0 and not current_delegate_list:
                            print('current_index == 0 and not current_delegate_list error\n\n\n')
                            return
                    else:
                        print(delegate_rate)
                        return
            else:
                print("error: index 0 not coinbase")
                raise ValueError()

            if current_height % 100000 == 0:
                print('current_height ', current_height)
            current_height += 1
            if 'nextblockhash' not in current_block_info:
                break
            next_block_hash = current_block_info['nextblockhash']

        print(current_delegate_address, current_index)
        print(current_delegate)
        print(delegate_rate)
        update_delegate_list = []
        for _delegate in delegate_rate:
            delegate_rate[_delegate]['status'] = 1  # 0: not working, 1: normal
            delegate_rate[_delegate]['active'] = 0  # 0: waiting, 1: block producting
            delegate_rate[_delegate]['_id'] = _delegate
            update_delegate_list.append(delegate_rate[_delegate])
        #print(len(update_delegate_list))
        #print(update_delegate_list[0])
        update_all_delegate(update_delegate_list)
        current_delegate_info = {'current_delegate': current_delegate, 'index': current_index}
        update_block_status(REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE, current_delegate_info)

    except Exception as e:
        print(e)
        raise


def parse_lbtc_block_main():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
        best_block_hash = rpc_connection.getbestblockhash()
        best_block = rpc_connection.getblock(best_block_hash)
        best_height = best_block['height'] - 18
        # best_height = 14
        block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)
        if not block_status:
            block_status = {"height": 1}
            update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, block_status)
        current_height = block_status['height']
        # print('start from height ', current_height)
        next_block_hash = ''
        while current_height <= best_height:
            current_mongo_add_tx_ids = []
            if not next_block_hash:
                next_block_hash = rpc_connection.getblockhash(current_height)
            current_block_info = rpc_connection.getblock(next_block_hash)
            if not current_block_info:
                break

            current_delegate_mysql = get_block_status(REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE)
            #current_delegate_mysql = None
            current_delegate_address = None
            current_delegate_list = []
            not_working_delegate = []
            current_index = ''
            tx_info = rpc_connection.gettransactionnew(current_block_info['tx'][0])
            if 'coinbase' in tx_info['vin'][0]:
                for _vout in tx_info['vout']:
                    if 'delegates' in _vout:
                        current_delegate_list = _vout['delegates']
                    else:
                        pass
                if tx_info['vout'][0]['scriptPubKey']['type'] == 'pubkeyhash' or \
                   tx_info['vout'][0]['scriptPubKey']['type'] == 'scripthash':
                    if len(tx_info['vout'][0]['scriptPubKey']['addresses']) != 1:
                        raise ValueError('vout multi addresses')
                    current_delegate_address = tx_info['vout'][0]['scriptPubKey']['addresses'][0]
                    if current_delegate_list:
                        current_index = current_delegate_list.index(current_delegate_address)
                    else:
                        current_index = current_delegate_mysql['current_delegate'].index(current_delegate_address)
                    if current_index > current_delegate_mysql['index']:
                        if current_index - current_delegate_mysql['index'] == 1:
                            not_working_delegate = []
                        else:
                            for _index in range(current_delegate_mysql['index'] + 1, current_index):
                                not_working_delegate.append(current_delegate_mysql['current_delegate'][_index])
                    else:
                        for _index in range(current_delegate_mysql['index'] + 1, 101):
                            not_working_delegate.append(current_delegate_mysql['current_delegate'][_index])
                        if current_delegate_list:
                            for _index in range(0, current_index):
                                not_working_delegate.append(current_delegate_list[_index])
                        else:
                            pass
                else:
                    raise ValueError()
            else:
                print("error: index 0 not coinbase")
                raise ValueError()
            # print(current_delegate_address, current_delegate_list, current_index, not_working_delegate)
            if current_index == 0 and not current_delegate_list:
                print('current_index == 0 and not current_delegate_list error\n\n\n')
                return
                #raise ValueError('current_index == 0 and not current_delegate_list error')
            if not_working_delegate:
                print('current_height: ', current_height, current_delegate_address, current_index,
                      'current_delegate_list: ', current_delegate_list, current_delegate_mysql, 'not_working_delegate: ', not_working_delegate)
                if len(not_working_delegate) > 1:
                    print('many_not_working_delegate')

            '''
            current_height += 1
            if 'nextblockhash' not in current_block_info:
                break
            next_block_hash = current_block_info['nextblockhash']
            current_delegate_mysql_new = {}
            current_delegate_mysql_new['index'] = current_index
            if current_delegate_list:
                current_delegate_mysql_new['current_delegate'] = current_delegate_list
            else:
                current_delegate_mysql_new['current_delegate'] = current_delegate_mysql['current_delegate']
            update_block_status(REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE, current_delegate_mysql_new)
            continue
            '''

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
                tx_id_to_raw_tx_info[_tx_id] = tx_info
                for _vin in tx_info['vin']:
                    if 'coinbase' in _vin:
                        pass
                    else:
                        vin_tx_id.append(_vin['txid'])
                vout_index = 0
                for _vout in tx_info['vout']:
                    if _vout['n'] != vout_index:
                        raise(ValueError('vout index error'))
                    if _vout['scriptPubKey']['type'] == 'pubkeyhash' or \
                       _vout['scriptPubKey']['type'] == 'scripthash':
                        if len(_vout['scriptPubKey']['addresses']) != 1:
                            raise ValueError('vout multi addresses')
                        tx_mongo['output'] += [_vout['n'], _vout['scriptPubKey']['addresses'][0],
                                               str(_vout['value'])]
                    elif _vout['scriptPubKey']['type'] == 'nulldata':
                        tx_mongo['output'] += [_vout['n'], 'nulldata', str(_vout['value'])]
                    else:
                        raise(ValueError('vout type unknow'))
                    vout_index += 1
                tx_mongos.append(tx_mongo)
                current_mongo_add_tx_ids.append(tx_mongo['_id'])
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
                        _tx_info_mongo['input'] += \
                            [old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 1],
                             old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 2]]

            try:
                add_many_tx(tx_mongos)
                current_block_info['tx_num'] = len(current_block_info['tx'])
                add_block_info(current_block_info)
            except Exception as e:
                print('add_many_tx add_block_info failed, current_height ', current_height, e)
                delete_many_tx(current_mongo_add_tx_ids)
                delete_block_info(current_block_info['height'])
                raise

            need_update = []
            for item in tx_mongos:
                for i in range(0, len(item['input']) // 2):
                    if item['input'][2*i] == 'coinbase':
                        continue
                    need_update.append({'address': item['input'][2*i],
                                        'amount': 0 - Decimal(item['input'][2*i + 1]),
                                        'time': item['time'],
                                        'hash': item['_id']})
                for i in range(0, len(item['output']) // 3):
                    if item['output'][3*i + 1] == 'nulldata':
                        continue
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
                            need_update_merge[item['hash']][item['address']] = \
                                Decimal(item['amount'])
                        else:
                            need_update_merge[item['hash']][item['address']] += \
                                Decimal(item['amount'])
            if need_update_merge:
                need_update = []
                for _hash in need_update_merge:
                    for _address in need_update_merge[_hash]:
                        need_update.append({'address': _address,
                                            'amount': need_update_merge[_hash][_address],
                                            'time': tx_time,
                                            'hash': _hash
                                            })
            if current_height % 1000 == 0:
                print('current_height ', current_height)
            #print('current_height ', current_height)
            current_height += 1
            update_many_address_info(need_update, PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT,
                                     {'height': current_height},
                                     current_delegate_address, current_delegate_list,
                                     current_index, not_working_delegate, current_delegate_mysql,
                                     REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE)
            if 'nextblockhash' not in current_block_info:
                break
            next_block_hash = current_block_info['nextblockhash']
    except Exception as e:
        print('get Exception: ', e)
        raise


@singleton('/tmp/parse_lbtc_block.pid')
def parse_lbtc_block():
    while(True):
        config_file = open('exit_parse', 'rU')
        for line in config_file.readlines():
            if(int(line)):
                print('exit_parse exit')
                config_file.close()
                exit()
        parse_lbtc_block_main()
        time.sleep(0.1)


if __name__ == '__main__':
    #parse_lbtc_delegate()
    parse_lbtc_block()
    #parse_lbtc_block_main()
