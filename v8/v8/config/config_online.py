#!/usr/bin/python3
# -*- coding: utf-8 -*-

# grant all privileges on *.* to lbtc@'%' identified by 'sxfMd4_f12508ccsdfdf';
DEBUG = False

MYSQLS = {
    'base': {
        'db': 'lbtcnode',
        'user': 'lbtc',
        'passwd': 'sxfMd4_f12508ccsdfdf',
        'host': 'localhost',
        'port': 3306,
    },
}

MONGO = {
    'base': {
        'host': '127.0.0.1:27017',
        'connect_timeout': 5000,
    },
}
