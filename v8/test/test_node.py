#!/usr/bin/python
# -*- coding: utf-8 -*-

from v8.config import config, config_online
from v8.engine.handlers.node_handler import get_all_node, add_or_update_node, update_node

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
    try:
        add_or_update_node(ip, user_agent, location, network, height, pix, status)
    except Exception as e:
        print(e)
    node_info = {'user_agent': user_agent,
                 'location': location,
                 'network': network,
                 'height': height,
                 'pix': pix,
                 'status': status,
                 'deleted': 0,
                 }
    print(update_node(ip, node_info))
    print('nodes num: ', len(get_all_node()))


if __name__ == '__main__':
    test_node()
