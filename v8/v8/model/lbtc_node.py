#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Float, Numeric
from sqlalchemy.ext.declarative import declarative_base

import hashlib

BaseModel = declarative_base()


class LbtcNode(BaseModel):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True)
    ip = Column(String)
    user_agent = Column(String)
    services = Column(String)
    location = Column(String)
    timezone = Column(String)
    network = Column(String)
    asn = Column(String)
    height = Column(Integer)
    pix = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    status = Column(Integer)
    deleted = Column(Integer)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    

class NodeNotValid(BaseModel):
    __tablename__ = 'node_not_valid'

    id = Column(Integer, primary_key=True)
    ip = Column(String)
    count = Column(Integer)
    create_time = Column(DateTime)


class NodeDistribution(BaseModel):
    __tablename__ = 'node_distribution'

    id = Column(Integer, primary_key=True)
    country = Column(String)
    rank = Column(Integer)
    node_num = Column(Integer)
    node_persent = Column(Float)
    deleted = Column(Integer)
    

class BlockStatus(BaseModel):
    __tablename__ = 'block_status'

    id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class BlockInfo(BaseModel):
    __tablename__ = 'block_info'
    
    height = Column(Integer, primary_key=True)
    hash = Column(String)
    tx_num = Column(Integer)
    strippedsize = Column(Integer)
    create_time = Column(DateTime)


class AddressInfo(BaseModel):
    __tablename__ = 'address_info'

    id = Column(Integer, primary_key=True)
    address = Column(String)
    balance = Column(Numeric(30, 15))
    receive = Column(Numeric(30, 15))
    send = Column(Numeric(30, 15))
    tx_num = Column(Integer)
    create_time = Column(DateTime)


address_tx = dict()



def gen_address_tx_model(address):
    hl = hashlib.md5()
    hl.update(address.encode(encoding='utf-8'))
    address = int(hl.hexdigest()[-2:], 16)
    table_name = 'zz_address_tx_%03d' % address
    print(table_name)
    cls_name = 'AddressTx_%03d' % address

    if table_name not in address_tx:
        cls_dict = {
            '__tablename__': table_name,
            
            'id': Column(Integer, primary_key=True),
            'hash': Column(String),
            'address': Column(String),
        }
        address_tx[table_name] = type(cls_name, (BaseModel, ), cls_dict)
    return address_tx[table_name]
