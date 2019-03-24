#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


BaseModel = declarative_base()


class User(BaseModel):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email_address = Column(String)
    password = Column(String)
    deleted = Column(Integer)
    is_admin = Column(Integer)
    device_type_ids = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
