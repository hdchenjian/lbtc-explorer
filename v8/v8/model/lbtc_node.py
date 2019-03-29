#!/usr/bin/python3
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


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


class LbtcTX(Document):
    class InputAddress(Document):
        structure = {
            'address': basestring,
            'station_price': float,
            'settlement_price': float,
            'weiche_price': float,
            'recent_user_weiche_price': float,
            'old_user_weiche_price': float,
            'device_nums': [basestring],
            'weiche_price_summary': basestring,
            'recent_user_weiche_price_summary': basestring,
            'old_user_weiche_price_summary': basestring,
            'regular_weiche_price': float,
            'regular_weiche_price_summary': basestring,
            'old_user_regular_weiche_price': float,
            'old_user_regular_weiche_price_summary': basestring,
        }

        default_values = {
            'oil_name': '',
            'station_price': 0,
            'weiche_price': 0,
            'recent_user_weiche_price': 0,
            'old_user_weiche_price': 0,
            'device_nums': [],
            'max_oil_discount_amount': 0,
            'weiche_price_summary': '',
            'recent_user_weiche_price_summary': '',
            'old_user_weiche_price_summary': '',
            'regular_weiche_price_summary': '',
            'old_user_regular_weiche_price_summary': '',
        }

    class _Person(Document):
        structure = {
            'name': basestring,
            'phone': basestring,
        }

        default_values = {
            'name': '',
            'phone': '',
        }

    structure = {
        'id': int,
        'shop_id': basestring,
        'brand': basestring,  # '', 'weiche', 'zhonghua', 'waiting'
        'name': basestring,
        'latitude': float,
        'longitude': float,
        'address': basestring,
        'phone': basestring,
        'city_id': int,
        'icon_url': basestring,
        'rate': int,
        'create_time': int,
        'update_time': int,
        'deleted': int,
        'online': int,
        'ok619_id': basestring,
        'oils': [_Oil],
        'opening_time': basestring,
        'oil_price_update_time': int,
        'weiche_prices': dict,
        'recent_user_weiche_prices': dict,
        'old_user_weiche_prices': dict,
        'min_weiche_pirce': float,
        'recent_user_min_weiche_price': float,
        'old_user_min_weiche_price': float,
        'oil_names': [basestring],
        'min_balance': float,
        'contact': _Person,
        'director': _Person,
        'direct_payment_available': bool,
        'new_oil_station': bool,
        'new_oil_station_start_time': int,
        'new_oil_station_end_time': int,
        'immune': bool,
        'vip_privilege_available': bool,
        'support_brabus': bool
    }

    default_values = {
        'deleted': 0,
        'direct_payment_available': False,
        'oils': [],
        'shop_id': '',
        'brand': '',
        'opening_time': '',
        'oil_price_update_time': 0,
        'new_oil_station': False,
        'new_oil_station_start_time': 0,
        'new_oil_station_end_time': 0,
        'update_time': 0,
        'min_balance': 0,
        'contact': _Person,
        'director': _Person,
        'immune': False,
        'vip_privilege_available': False,
        'support_brabus': False
    }
