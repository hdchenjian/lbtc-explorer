#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time
from decimal import Decimal

from v8.config import config, config_online
from v8.engine.handlers.node_handler import find_many_tx, update_block_status, \
    get_block_status, add_block_info, update_many_address_info, add_many_tx, \
    update_all_delegate, update_all_committee, update_all_proposal, \
    update_most_rich_address, update_network_tx_statistics
from bitcoinrpc.authproxy import AuthServiceProxy

from decorators import singleton
from config import PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, \
    REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME, REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO, \
    REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST, REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME, \
    REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS, \
    REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS, REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS

config.from_object(config_online)


def parse_lbtc_block_main():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    try:
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
            # print(current_block_info)
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
                # print(tx_info)
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
                # print(tx_mongo)
                # tx_mongo['output'].sort(key=lambda x: x[0])
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
                        _tx_info_mongo['input'] += \
                            [old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 1],
                             old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 2]]

            # print(current_block_info)
            add_many_tx(tx_mongos)

            current_block_info['tx_num'] = len(current_block_info['tx'])
            add_block_info_result = add_block_info(current_block_info)
            if not add_block_info_result:
                print('add_block_info failed, current_height ', current_height)
                break

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
            update_many_address_info(need_update)

            print('current_height ', current_height)
            current_height += 1
            # exit()

            for item in tx_mongos:
                for i in range(0, len(item['input']) // 2):
                    if item['input'][2*i] == 'coinbase':
                        pass
                        # coinbase_address.append(item['output'][1])
        update_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, {'height': current_height})
        # update_many_delegate_active(coinbase_address)
    except Exception as e:
        print(e)
        raise


def query_all_delegate():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))

    list_delegate = rpc_connection.listdelegates()
    delegate_address_to_name = {}
    delegate_name_to_address = {}
    all_delegate = []
    for _delegate in list_delegate:
        _delegate_info = {}
        _delegate_info['_id'] = _delegate['address']
        _delegate_info['name'] = _delegate['name']
        delegate_address_to_name[_delegate['address']] = _delegate['name']
        delegate_name_to_address[_delegate['name']] = _delegate['address']
        _delegate_info['funds'] = \
            str(Decimal(rpc_connection.getdelegatefunds(_delegate['name'])) / 100000000)
        _delegate_info['votes'] = \
            str(Decimal(rpc_connection.getdelegatevotes(_delegate['name'])) / 100000000)
        _delegate_info['active'] = False
        all_delegate.append(_delegate_info)
        # _delegate['votes_address'] = rpc_connection.listreceivedvotes(_delegate['name'])
    all_delegate.sort(key=lambda x: Decimal(x['votes']), reverse=True)
    index = 2
    for _delegate in all_delegate:
        _delegate['index'] = index
        index += 1
    update_all_delegate(all_delegate)
    update_block_status(REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME, delegate_address_to_name)
    update_block_status(REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS, delegate_name_to_address)


def query_all_committee_proposal():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))

    committee_address_map = {}
    all_committee = []
    index = 1
    committee_address_to_name = {}
    committee_name_to_address = {}
    for _committee in rpc_connection.listcommittees():
        _committee_detail = rpc_connection.getcommittee(_committee['address'])
        _committee['votes'] = _committee_detail['votes']
        _committee['index'] = index
        index += 1
        all_committee.append(_committee)
        committee_address_map[_committee['address']] = _committee
        committee_address_to_name[_committee['address']] = _committee['name']
        committee_name_to_address[_committee['name']] = _committee['address']
    update_all_committee(all_committee)
    update_block_status(REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME, committee_address_to_name)
    update_block_status(REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS, committee_name_to_address)

    all_proposal = []
    all_bill = rpc_connection.listbills()
    index = 1
    for _bill in all_bill:
        _bill_detail = rpc_connection.getbill(_bill['id'])

        _proposal = {}
        _proposal['index'] = index
        index += 1
        _proposal['id'] = _bill['id']
        _proposal['title'] = _bill['title']
        _proposal['detail'] = _bill_detail['detail']
        _proposal['start_time'] = datetime.datetime.fromtimestamp(_bill_detail['starttime'])
        _proposal['end_time'] = datetime.datetime.fromtimestamp(_bill_detail['endtime'])
        _proposal['state'] = _bill_detail['state']
        _proposal['options'] = _bill_detail['options']
        _proposal['url'] = _bill_detail['url']
        _proposal['committee'] = _bill_detail['committee']
        _proposal['committee_name'] = committee_address_map[_proposal['committee']]['name']

        _proposal_voters = rpc_connection.listbillvoters(_proposal['id'])
        option_index = 0
        for option in _proposal['options']:
            for vote in _proposal_voters:
                if vote['index'] == option_index:
                    sum_vote = Decimal(0)
                    address_list = []
                    for _address in vote['addresses']:
                        sum_vote += _address['votes']
                        address_list.append(_address['voters'])
                    option['votes'] = str(sum_vote / Decimal(100000000))
                    option['vote_address'] = address_list
                    break
            option_index += 1
        all_proposal.append(_proposal)
    update_all_proposal(all_proposal)


def get_timedelta_network_tx_statistics(days):
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    best_block_hash = rpc_connection.getbestblockhash()
    # best_block_hash = '2c0cacfacbe2081767230f16a403ec88d78173163187a8e0296eba744916077f ' #  todo
    current_block_info = rpc_connection.getblock(best_block_hash)
    end_time = datetime.datetime.fromtimestamp(current_block_info['time'])
    start_time = int((end_time - datetime.timedelta(days=days)).timestamp())
    previous_block_hash = ''
    block_count = 0
    block_size = 0
    tx_num = 0
    tx_ids = []
    while True:
        if previous_block_hash:
            current_block_info = rpc_connection.getblock(previous_block_hash)
            if current_block_info['time'] < start_time:
                break
        previous_block_hash = current_block_info['previousblockhash']
        block_count += 1
        tx_num += len(current_block_info['tx'])
        block_size += current_block_info['strippedsize']
        tx_ids += current_block_info['tx']

    avg_fee = Decimal(0)
    avg_fee_num = 0
    _tx_list = find_many_tx(tx_ids)
    # print(len(tx_ids), len(_tx_list))

    for _tx_item in _tx_list:
        if _tx_item['input'][0] == 'coinbase':
            lbtc_input = '0'
        else:
            lbtc_input = Decimal(0)
            for i in range(0, len(_tx_item['input']) // 2):
                lbtc_input += Decimal(_tx_item['input'][2*i + 1])

        lbtc_output = Decimal(0)
        for i in range(0, len(_tx_item['output']) // 3):
            if _tx_item['output'][3*i + 1] == 'nulldata':
                continue
            lbtc_output += Decimal(_tx_item['output'][3*i + 2])
        if lbtc_input == '0':
            pass
        else:
            avg_fee += (lbtc_input - lbtc_output)
            avg_fee_num += 1

    if avg_fee_num > 0:
        avg_fee = float(avg_fee) / float(avg_fee_num)
    else:
        avg_fee = 0

    tx_speed = float(tx_num) / float(days * 24 * 3600)
    block_size_avg = float(block_size) / float(block_count)
    tx_num_no_coinbase = tx_num - block_count
    return block_size_avg, tx_speed, tx_num_no_coinbase, avg_fee


def update_network_tx_statistics_function():
    block_size_avg_24h, tx_speed_24h, tx_num_no_coinbase_24h, avg_fee_24h = \
        get_timedelta_network_tx_statistics(1)
    block_size_avg_14d, tx_speed_14d, tx_num_no_coinbase_14d, avg_fee_14d = \
        get_timedelta_network_tx_statistics(14)
    network_tx_statistics = {
        'block_size_avg_24h': block_size_avg_24h,
        'tx_speed_24h': tx_speed_24h,
        'tx_num_no_coinbase_24h': tx_num_no_coinbase_24h,
        'avg_fee_24h': avg_fee_24h,
        'block_size_avg_14d': block_size_avg_14d,
        'tx_speed_14d': tx_speed_14d,
        'tx_num_no_coinbase_14d': tx_num_no_coinbase_14d,
        'avg_fee_14d': avg_fee_14d,
    }
    update_network_tx_statistics(REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS, network_tx_statistics)


@singleton('/tmp/parse_lbtc_block.pid')
def parse_lbtc_block():
    update_most_rich_address_time = None
    update_network_tx_statistics_time = None
    while(True):
        query_all_committee_proposal()
        time_now = datetime.datetime.now()
        if update_most_rich_address_time is None or \
           (time_now - update_most_rich_address_time).total_seconds() > 100:
            update_most_rich_address(REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST, top=100)
            update_most_rich_address_time = time_now

        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
        tx_out_set_info = rpc_connection.gettxoutsetinfo()
        for key in ['bestblock', 'hash_serialized', 'txouts', 'bytes_serialized']:
            tx_out_set_info.pop(key)
        tx_out_set_info['total_amount'] = str(tx_out_set_info['total_amount'])
        update_block_status(REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO, tx_out_set_info)

        # if random.random() > 0.1:
        query_all_delegate()

        if update_network_tx_statistics_time is None or \
           (time_now - update_network_tx_statistics_time).total_seconds() > 3600:
            update_network_tx_statistics_function()
            update_network_tx_statistics_time = time_now

        break
        parse_lbtc_block_main()
        break
        time.sleep(2)


if __name__ == '__main__':
    update_network_tx_statistics_function()
    # parse_lbtc_block()
