#!/usr/bin/python3
# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, \
    add_not_valid_node, delete_not_valid_node, get_all_not_valid_node, add_many_tx, \
    add_one_tx, update_one_tx, find_one_tx

config.from_object(config_online)

def test_mongo():
    tx = {'_id': '1234', 'au': '1',
          'time': datetime.datetime.now(),
          'input': ['input_address', str(Decimal('0.1')), 'input_address1', str(Decimal('0.1'))],
          'output': ['output_address', str(Decimal('0.1')),'output_address1', str(Decimal('0.1'))]}
    #print(add_one_tx(tx))
    #print(update_one_tx(tx))
    print(find_one_tx('f6f72448d1c87fcc5720f4e6b756981f5a7b866ed966c3166229779a5652c30b'))
    

def test_node():
    ip = '120.79.161.218:9333'
    user_agent = '/Satoshi:0.14.2/'
    location = 'China'
    network = 'Hangzhou Alibaba Advertising Co.,Ltd.:AS37963'
    height = 4608395
    pix = 0.5
    status = 1
    deleted = 0
    
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


if __name__ == '__main__':
    #test_node()
    #test_not_valid_node()
    test_mongo()
