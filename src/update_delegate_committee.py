#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time
from decimal import Decimal

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


def query_all_delegate_local():
    rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
    tx_out_set_info = rpc_connection.gettxoutsetinfo()
    for key in ['bestblock', 'hash_serialized', 'bytes_serialized']:
        tx_out_set_info.pop(key)
    tx_out_set_info['total_amount'] = str(tx_out_set_info['total_amount'])
    update_block_status(REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO, tx_out_set_info)

    list_delegate = rpc_connection.listdelegates()
    delegate_address_to_name = {'166D9UoFdPcDEGFngswE226zigS8uBnm3C': 'LBTCSuperNode'}
    delegate_name_to_address = {'LBTCSuperNode': '166D9UoFdPcDEGFngswE226zigS8uBnm3C'}
    all_delegate = [{'_id': '166D9UoFdPcDEGFngswE226zigS8uBnm3C',
                     'funds': '0', 'votes': '21000000', 'name': 'LBTCSuperNode'}]
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
        all_delegate.append(_delegate_info)
        # _delegate['votes_address'] = rpc_connection.listreceivedvotes(_delegate['name'])
    all_delegate.sort(key=lambda x: Decimal(x['votes']), reverse=True)
    index = 1
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


def update_network_tx_statistics_function(days):
    if days == 1:
        block_size_avg_24h, tx_speed_24h, tx_num_no_coinbase_24h, avg_fee_24h = \
            get_timedelta_network_tx_statistics(1)
        network_tx_statistics = {
            'block_size_avg_24h': block_size_avg_24h,
            'tx_speed_24h': tx_speed_24h,
            'tx_num_no_coinbase_24h': tx_num_no_coinbase_24h,
            'avg_fee_24h': avg_fee_24h,
        }
        update_network_tx_statistics(REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS,
                                     network_tx_statistics)

    else:
        block_size_avg_14d, tx_speed_14d, tx_num_no_coinbase_14d, avg_fee_14d = \
            get_timedelta_network_tx_statistics(14)
        network_tx_statistics = {
            'block_size_avg_14d': block_size_avg_14d,
            'tx_speed_14d': tx_speed_14d,
            'tx_num_no_coinbase_14d': tx_num_no_coinbase_14d,
            'avg_fee_14d': avg_fee_14d,
        }
        update_network_tx_statistics(REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS,
                                     network_tx_statistics)

@singleton('/tmp/update_delegate_committee.pid')
def update_delegate_committee():
    update_most_rich_address_time = None
    update_network_tx_statistics_time_1_day = None
    update_network_tx_statistics_time_14_day = None
    update_address_growth_daily_info_time = None
    query_all_delegate_time = None

    while(True):    
        time_now = datetime.datetime.now()
        if update_address_growth_daily_info_time is None or \
           (time_now - update_address_growth_daily_info_time).total_seconds() > 300:
            update_address_growth_daily_info()
            update_transaction_daily_info()
            update_address_growth_daily_info_time = time_now

        if update_most_rich_address_time is None or \
           (time_now - update_most_rich_address_time).total_seconds() > 100:
            update_most_rich_address(REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST, top=100)
            update_most_rich_address_time = time_now

        if query_all_delegate_time is None or \
           (time_now - query_all_delegate_time).total_seconds() > 60:
            query_all_delegate_local()
            query_all_committee_proposal()
            query_all_delegate_time = time_now

        if update_network_tx_statistics_time_1_day is None or \
           (time_now - update_network_tx_statistics_time_1_day).total_seconds() > 300:
            update_network_tx_statistics_function(1)
            update_network_tx_statistics_time_1_day = time_now
        if update_network_tx_statistics_time_14_day is None or \
           (time_now - update_network_tx_statistics_time_14_day).total_seconds() > 3600 * 6:
            update_network_tx_statistics_function(14)
            update_network_tx_statistics_time_14_day = time_now
        time.sleep(1)
        break


if __name__ == '__main__':
    #parse_lbtc_delegate()
    update_delegate_committee()
