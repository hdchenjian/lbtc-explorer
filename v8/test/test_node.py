#!/usr/bin/python3
# -*- coding: utf-8 -*-

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, update_or_add_node, \
    add_not_valid_node, delete_not_valid_node, get_all_not_valid_node

config.from_object(config_online)

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
    test_not_valid_node()
