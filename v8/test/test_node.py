#!/usr/bin/python
# -*- coding: utf-8 -*-

from v8.config import config, config_test, config_online
from v8.engine.handlers.node_handler import get_all_node, add_node, update_node

test = True
if test:
    config.from_object(config_test)
    print("test environment")
else:
    config.from_object(config_online)
    print("online environment")


def test_node():
    ip = '120.78.147.20:9333'
    user_agent = '/Satoshi:0.14.2/'
    location = 'China'
    network = 'Hangzhou Alibaba Advertising Co.,Ltd.:AS37963'
    height = 4608395
    pix = 0.5
    status = 1
    try:
        add_node(ip, user_agent, location, network, height, pix, status)
    except Exception as e:
        print(e)
    node_info = {'user_agent': user_agent,
                 'location': location,
                 'network': network,
                 'height': height,
                 'pix': pix,
                 'status': status
                 }
    print(update_node(ip, node_info))
    print(get_all_node())


if __name__ == '__main__':
    test_node()
