#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base


BaseModel = declarative_base()


class LbtcNode(BaseModel):
    __tablename__ = 'node'

    id = Column(Integer, primary_key=True)
    ip = Column(String)
    user_agent = Column(Integer)
    location = Column(Integer)
    network = Column(Integer)
    height = Column(Integer)
    pix = Column(Float)
    status = Column(Integer)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
    
