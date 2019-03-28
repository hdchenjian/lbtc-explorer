#!/usr/bin/python
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
