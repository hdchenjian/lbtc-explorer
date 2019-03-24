#!/usr/bin/python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


BaseModel = declarative_base()


class FirmInfo(BaseModel):
    __tablename__ = 'firm_info'

    id = Column(Integer, primary_key=True)
    device_type = Column(Integer)
    firm_version = Column(String)
    firm_url = Column(String)
    online = Column(Integer)
    deleted = Column(Integer)
    md5 = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class AlgorithmInfo(BaseModel):
    __tablename__ = 'algorithm_info'

    id = Column(Integer, primary_key=True)
    device_type = Column(Integer)
    alg_version = Column(String)
    alg_url = Column(String)
    online = Column(Integer)
    deleted = Column(Integer)
    md5 = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class FpgaInfo(BaseModel):
    __tablename__ = 'fpga_info'

    id = Column(Integer, primary_key=True)
    device_type = Column(Integer)
    fpga_version = Column(String)
    fpga_url = Column(String)
    online = Column(Integer)
    deleted = Column(Integer)
    md5 = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class DeviceInfo(BaseModel):
    __tablename__ = 'device_info'

    id = Column(Integer, primary_key=True)
    device_id = Column(String)
    device_type = Column(Integer)
    alg_version = Column(String)
    alg_version_target = Column(Integer)
    alg_version_use_confirm = Column(Integer)
    firm_version = Column(String)
    firm_version_target = Column(Integer)
    firm_version_use_confirm = Column(Integer)
    fpga_version = Column(String)
    fpga_version_target = Column(String)
    fpga_version_use_confirm = Column(Integer)
    p2p = Column(Integer)
    deleted = Column(Integer)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class UpdateRule(BaseModel):
    __tablename__ = 'update_rule'

    id = Column(Integer, primary_key=True)
    version = Column(String)
    version_target = Column(String)
    update_type = Column(Integer)
    device_type = Column(Integer)
    use_confirm = Column(Integer)
    online = Column(Integer)
    deleted = Column(Integer)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class Config(BaseModel):
    __tablename__ = 'config'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class FpgaVersionMap(BaseModel):
    __tablename__ = 'fpga_version_map'

    id = Column(Integer, primary_key=True)
    version = Column(String)
    version_number = Column(String)
    device_type = Column(Integer)
    online = Column(Integer)
    deleted = Column(Integer)
    create_time = Column(DateTime)
    update_time = Column(DateTime)


class DeviceType(BaseModel):
    __tablename__ = 'device_type'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    device_name = Column(String)
    create_time = Column(DateTime)
    update_time = Column(DateTime)
