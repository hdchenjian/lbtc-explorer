#!/usr/bin/python3
# -*- coding: utf-8 -*-


from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, \
    add_not_valid_node, delete_not_valid_node, get_all_not_valid_node, add_many_tx, \
    add_one_tx, find_one_tx, query_all_committee, query_all_delegate, query_all_proposal, \
    query_coinbase_tx, update_address_info_update_time, update_address_growth_daily_info, \
    update_transaction_daily_info, get_balance_distribution

config.from_object(config_online)


def test_mongo():
    print(find_one_tx('f6f72448d1c87fcc5720f4e6b756981f5a7b866ed966c3166229779a5652c30b'))


def test_node():
    ip = '120.79.161.218:9333'
    user_agent = '/Satoshi:0.14.2/'
    location = 'China'
    network = 'Hangzhou Alibaba Advertising Co.,Ltd.:AS37963'
    height = 4608395
    pix = 0.5
    status = 1

    node_info = {'user_agent': user_agent,
                 'location': location,
                 'network': network,
                 'height': height,
                 'pix': pix,
                 'status': status,
                 'deleted': 0,
                 }
    print(update_or_add_node(ip, node_info))
    print('nodes num: ', len(get_all_node()))


def test_not_valid_node():
    add_not_valid_node('127.0.0.1:9333')
    all_node = get_all_not_valid_node()
    print(all_node)
    delete_not_valid_node(all_node[0]['id'])


def test_get_balance_distribution():
    address_distribution = [[10000, 99999999],
                            [1000, 10000],
                            [10, 1000],
                            [1, 10],
                            [0.1, 1],
                            [0.01, 0.1],
                            [0.001, 0.01],
                            [-1, 0.001]]

    print(get_balance_distribution(address_distribution))
    ret = get_balance_distribution(address_distribution)
    address_count = 0
    balance_total = 0
    address_stats = []
    balance_stats = []
    for i in range(0, len(address_distribution)):
        address_count += ret[2*i]
        address_stats.append(ret[2*i])
        balance_total += ret[2*i + 1]
        balance_stats.append(ret[2*i + 1])
    print(address_count, balance_total)
    print(ret[


if __name__ == '__main__':
    # test_node()
    # test_not_valid_node()
    # test_mongo()
    test_get_balance_distribution()
    #print(query_all_committee())
    # print(query_all_delegate())
    # print(query_all_proposal())
    # print(query_coinbase_tx(['8c7ee1999644b81200390a182a0b9e4f85574991cddb7b7235538f02b79d2c26'])[0])
    # update_address_info_update_time()
    # update_address_growth_daily_info()
    # update_transaction_daily_info('', '')
