#!/usr/bin/python3
# -*- coding: utf-8 -*-

import contextlib
import datetime
import json
from decimal import Decimal
import pymongo

from v8.engine import db_conn
from v8.model.lbtc_node import LbtcNode, NodeNotValid, NodeDistribution, BlockStatus, BlockInfo, \
    AddressInfo, gen_address_tx_model, AddressGrowthDaily, TransactionDaily
from v8.engine.util import model_to_dict

from v8.engine.handlers.node_handler import find_many_tx
from v8.config import config, config_online
config.from_object(config_online)

with contextlib.closing(db_conn.gen_session_class('base')()) as session:
    for _address_info in session.query(AddressInfo).order_by(AddressInfo.id.desc()):
        address = _address_info.address
        print(_address_info.id, _address_info.address, _address_info.balance)
        
        TransactionInfo = gen_address_tx_model(address)
        tx_ids = []
        for _transaction_info in session.query(TransactionInfo).filter(TransactionInfo.address == address):
            tx_ids.append(_transaction_info.hash)
        txs = find_many_tx(tx_ids)
        balance = Decimal(0)
        total_received = Decimal(0)
        total_send = Decimal(0)
        need_update = []
        for item in txs:
            for i in range(0, len(item['input']) // 2):
                if item['input'][2*i] == 'coinbase' or item['input'][2*i + 0] != address:
                    continue
                balance -= Decimal(item['input'][2*i + 1])
                total_send += Decimal(item['input'][2*i + 1])
            for i in range(0, len(item['output']) // 3):
                if item['output'][3*i + 1] == 'nulldata' or item['output'][3*i + 1] != address:
                    continue
                balance += Decimal(item['output'][3*i + 2])
                total_received += Decimal(item['output'][3*i + 2])
        if(_address_info.balance != balance):
            #print(txs[0])
            print('real balance: ', balance, len(tx_ids))
            print(total_received, total_send)
            break
    
