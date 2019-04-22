#!/usr/bin/python3
# -*- coding: utf-8 -*-


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient


mysql_url = \
    'mysql+pymysql://%(user)s:%(passwd)s@%(host)s:%(port)d/%(db)s?charset=utf8'
session_classes = dict()


def gen_session_class(conn_name):
    if conn_name not in session_classes:
        from v8.config import config
        cls = dict()
        cls['engine'] = create_engine(
            mysql_url % config['MYSQLS'][conn_name],
            echo_pool=True,
            echo=False,
            pool_size=30,
            pool_recycle=600
        )
        cls['cls'] = sessionmaker(bind=cls['engine'])
        session_classes[conn_name] = cls
    return session_classes[conn_name]['cls']


mongo_connections = dict()


def gen_mongo_connection(conn_name):
    if conn_name not in mongo_connections:
        from v8.config import config
        mongo_connection = MongoClient(host='localhost', port=27017, connect=False)
        mongo_connections[conn_name] = mongo_connection
    return mongo_connections[conn_name]
