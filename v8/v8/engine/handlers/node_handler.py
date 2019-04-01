#!/usr/bin/python3
# -*- coding: utf-8 -*-

import contextlib
import datetime
import json
from sqlalchemy.sql import func
from decimal import Decimal
import pymongo

from v8.engine import db_conn
from v8.model.lbtc_node import LbtcNode, NodeNotValid, NodeDistribution, BlockStatus, BlockInfo, \
    AddressInfo, gen_address_tx_model
from v8.engine.util import model_to_dict


def get_node_by_ip(ip):
    """Get node info.

    Args:
        ip (string): node ip

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _node = session.query(LbtcNode).filter(LbtcNode.ip == ip).first()
        if not _node:
            return None
        else:
            return model_to_dict(_node)


def get_all_node(node_status, country='', deleted_node=1):
    """Get node info.

    Args:
        node_status (int): 2: all node, 1: online node, 0: offline node

    Returns:
        list of node or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        filters = []
        if deleted_node != 1:
            filters.append(LbtcNode.deleted == 0)
        if(node_status != 2):
            filters.append(LbtcNode.status == node_status)
        if(country != ''):
            filters.append(LbtcNode.location.like('%' + country))
        for _node in session.query(LbtcNode) \
                            .filter(*filters) \
                            .order_by(LbtcNode.height.desc()):
            ret.append(model_to_dict(_node))
        return ret


def delete_node(ip):
    """delete node.

    Args:
        ip (string): node ip

    Returns:
        delete count or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        count = 0
        try:
            count = session.query(LbtcNode).filter(LbtcNode.ip == ip).delete()
            session.commit()
        except:
            session.rollback()
            raise
        return count


def update_or_add_node(ip, node_info):
    """Update node info, add it when ip not exist.

    Args:
        ip (string): ip and port, for example: 120.78.147.9333
        node_info (dict):
            user_agent (string): client version
            location (string): host location
            network (string): network status
            height (int): block height
            pix (float): calculated properties and network metrics every 24 hours
            status (int): 0: offline, 1: online
            deleted (int): 0: normal, 1: deleted
        
    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        time_now = datetime.datetime.now()
        _node = session.query(LbtcNode).filter(LbtcNode.ip == ip).first()
        try:
            if _node is None:
                _node = LbtcNode()
                _node.ip = ip
                _node.user_agent = ''
                _node.services = ''
                _node.location = ''
                _node.timezone = ''
                _node.network = ''
                _node.asn = ''
                _node.height = 0
                _node.pix = 0
                _node.latitude = 0
                _node.longitude = 0
                _node.status = 1
                _node.deleted = 0
                _node.create_time = time_now
                session.add(_node)
            for _key in ['user_agent', 'services', 'location', 'timezone', 'network', 'asn',
                         'height', 'pix', 'status', 'deleted', 'latitude', 'longitude']:
                if _key in node_info:
                    setattr(_node, _key, node_info[_key])
            _node.update_time = time_now
            session.commit()
        except:
            session.rollback()
            raise
        return model_to_dict(_node)


def add_not_valid_node(ip):
    """Add a node.

    Args:
        ip (string): ip and port, for example: 120.78.147.20:9333

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            _node = NodeNotValid()
            _node.ip = ip
            _node.count = 0
            _node.create_time = datetime.datetime.now()
            session.add(_node)
            session.commit()
            return model_to_dict(_node)
        except:
            session.rollback()
            return None


def add_not_valid_node_connect_try_times(ip):
    """Update node info

    Args:
        ip (string): ip and port, for example: 120.78.147.9333
        
    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _node = session.query(NodeNotValid).filter(NodeNotValid.ip == ip).first()
        _node.count += 1
        session.commit()
        return model_to_dict(_node)


def delete_not_valid_node(node_ip):
    """delete node.

    Args:
        node_ip (string): node ip

    Returns:
        delete count or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        count = 0
        try:
            count = session.query(NodeNotValid).filter(NodeNotValid.ip == node_ip).delete()
            session.commit()
        except:
            session.rollback()
            raise
        return count


def get_all_not_valid_node():
    """Get node info.

    Args:

    Returns:
        list of node.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _node in session.query(NodeNotValid):
            ret.append(model_to_dict(_node))
        return ret


def get_node_distribution(limit_count=7):
    """Get node distribution.

    Args:

    Returns:
        list of node.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _node in session.query(NodeDistribution) \
                            .filter(NodeDistribution.deleted == 0) \
                            .order_by(NodeDistribution.node_num.desc()) \
                            .limit(limit_count):
            ret.append(model_to_dict(_node))
        return ret


def update_node_distribution(country_info):
    """Update node distribution info, add it when not exist.

    Args:
        country_info (dict):
            country (string): country name
            rank (int): 
            node_num (int): 
            node_persent (float): 
        
    Returns:
        dict of node info or None.
    """
    if not country_info: return False
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        for _node in session.query(NodeDistribution).filter(~NodeDistribution.country.in_(country_info.keys())):
            _node.deleted = 1
            session.commit()
        try:
            for country_name in country_info:
                _country = session.query(NodeDistribution).filter(NodeDistribution.country == country_name).first()
                if _country is None:
                    _country = NodeDistribution()
                    _country.country = country_name
                    _country.rank = 0
                    _country.node_num = 0
                    _country.node_persent = 0
                    _country.deleted = 0
                    session.add(_country)
                for _key in ['rank', 'node_num', 'node_persent']:
                    if _key in country_info[country_name]:
                        setattr(_country, _key, country_info[country_name][_key])
                _country.deleted = 0
                session.commit()
        except:
            session.rollback()
            raise
        return True


def get_block_status(key):
    """Get node distribution.

    Args:

    Returns:
        list of node.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _block_status = session.query(BlockStatus) \
                            .filter(BlockStatus.key == key) \
                            .first()
        if not _block_status:
            return None
        else:
            return json.loads(_block_status.value)


def get_block_status_multi_key(key_list):
    """Get node distribution.

    Args:

    Returns:
        list of node.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = {}
        for _block_status in session.query(BlockStatus).filter(BlockStatus.key.in_(key_list)):
            ret[_block_status.key] = json.loads(_block_status.value)
        return ret


def update_block_status(key, value):
    """Update node distribution info, add it when not exist.

    Args:
        key (string):
        value (dict):
        
    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            time_now = datetime.datetime.now()
            _block_status = session.query(BlockStatus).filter(BlockStatus.key == key).first()
            if _block_status is None:
                _block_status = BlockStatus()
                _block_status.key = key
                _block_status.create_time = time_now
                session.add(_block_status)
            _block_status.update_time = time_now
            _block_status.value = json.dumps(value)
            session.commit()
            return True
        except:
            session.rollback()
            raise


def add_many_tx(txs):
    """Add many tx.

    Args:
        txs (list): list of tx

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    result = conn.lbtc.lbtc_tx.insert_many(txs)
    return result.inserted_ids


                                      
def add_one_tx(tx):
    """Add one tx.

    Args:
        tx (dict): dict of tx

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    result = conn.lbtc.lbtc_tx.insert_one(tx)
    return result.inserted_id


def query_coinbase_tx(txs):
    """Add many tx.

    Args:
        txs (list): list of tx

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    ret = []
    for doc in conn.lbtc.lbtc_tx.find({'_id': {'$in': txs}, 'input' : ['coinbase', '']}):
        ret.append(doc)
    return ret


def find_one_tx(tx_id):
    """Find one tx.

    Args:
        tx_id (string): 

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    result = conn.lbtc.lbtc_tx.find_one({'_id': tx_id})
    return result


def find_many_tx(tx_ids):
    """Find one tx.

    Args:
        tx_ids (list): 

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    result = []
    for doc in conn.lbtc.lbtc_tx.find({ '_id': { '$in': tx_ids } }):
        result.append(doc)
    return result


def update_one_delegate(delegate):
    """Add one delegate.

    Args:
        tx (dict): dict of delegate

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    _delegate = conn.lbtc.lbtc_delegate.find_one({'_id': delegate['_id']})
    if _delegate is None:
        delegate['active'] = False
        result = conn.lbtc.lbtc_delegate.insert_one(delegate)
        return result.inserted_id
    else:
        modify_dict = {'funds': delegate['funds'],
                       'votes': delegate['votes'],
                       'votes_address': delegate['votes_address']
        }
        if 'active' in delegate:
            modify_dict['active'] = delegate['active']
        conn.lbtc.lbtc_delegate.update_one({'_id': delegate['_id']}, {'$set': modify_dict}, upsert=False)


def update_many_delegate_active(delegate_ids):
    """Add one delegate.

    Args:
        tx (dict): dict of delegate

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    conn.lbtc.lbtc_delegate.update_many({'_id': { '$in': delegate_ids}}, {'$set': {'active': True}}, upsert=False)


def update_all_committee(all_committee):
    """Add all committee.

    Args:
        tx (list): list of committee

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    for _committee in all_committee:
        conn.lbtc.lbtc_committee.update_one({'_id': _committee['address']}, {'$set': _committee}, upsert=True)


def update_all_proposal(all_proposal):
    """Add all proposal.

    Args:
        tx (list): list of proposal

    Returns:
        
    """
    conn = db_conn.gen_mongo_connection('base')
    for _proposal in all_proposal:
        conn.lbtc.lbtc_proposal.update_one({'_id': _proposal['id']}, {'$set': _proposal}, upsert=True)


def query_all_committee():
    """Add all committee.

    Args:

    Returns:
        tx (list): list of committee
        
    """
    conn = db_conn.gen_mongo_connection('base')
    ret = []
    for _committee in conn.lbtc.lbtc_committee.find().sort("index", pymongo.ASCENDING):
        ret.append(_committee)
    return ret


def query_all_proposal():
    """Add all proposal.

    Args:

    Returns:
        tx (list): list of proposal
        
    """
    conn = db_conn.gen_mongo_connection('base')
    ret = []
    for _proposal in conn.lbtc.lbtc_proposal.find().sort("index", pymongo.ASCENDING):
        ret.append(_proposal)
    return ret


def query_all_delegate():
    """Add all delegate.

    Args:

    Returns:
        tx (list): list of delegate
        
    """
    conn = db_conn.gen_mongo_connection('base')
    ret = []
    for _delegate in conn.lbtc.lbtc_delegate.find().sort("index", pymongo.ASCENDING):
        ret.append(_delegate)
    return ret


def add_block_info(block_info):
    """Add a node.

    Args:

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            _block_info = BlockInfo()
            for key in ['height', 'hash', 'tx_num', 'strippedsize']:
                setattr(_block_info, key, block_info[key])
            _block_info.create_time = datetime.datetime.fromtimestamp(block_info['time'])
            session.add(_block_info)
            session.commit()
            return model_to_dict(_block_info)
        except:
            session.rollback()
            return None


def update_address_info(address, amount, time):
    """Add a node.

    Args:

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            _address_info = session.query(AddressInfo).filter(AddressInfo.address == address).first()
            amount = Decimal(amount)
            if _address_info is None:
                _address_info = AddressInfo()
                _address_info.address = address
                _address_info.create_time = time
                _address_info.balance = 0
                _address_info.receive = 0
                _address_info.send = 0
                _address_info.tx_num = 0
                session.add(_address_info)
            if amount >= 0:
                 _address_info.balance += amount
                 _address_info.receive += amount
            else:
                _address_info.balance -= amount
                _address_info.send += amount
            _address_info.tx_num += 1
            session.commit()
            return True
        except:
            session.rollback()
            raise


def update_many_address_info(address_list):
    """Add a node.

    Args:

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            _address_info_match = []
            for tx_info in address_list:
                address = tx_info['address']
                amount = Decimal(tx_info['amount'])
                time = tx_info['time']
                _address_info = session.query(AddressInfo).filter(AddressInfo.address == address).first()
                if _address_info is None:
                    _address_info = AddressInfo()
                    _address_info.address = address
                    _address_info.create_time = time
                    _address_info.balance = 0
                    _address_info.receive = 0
                    _address_info.send = 0
                    _address_info.tx_num = 0
                    session.add(_address_info)
                _address_info_match.append(_address_info)
                if amount >= 0:
                     _address_info.balance += amount
                     _address_info.receive += amount
                else:
                    _address_info.balance += amount
                    _address_info.send += (0 - amount)
                _address_info.tx_num += 1

                TransactionInfo = gen_address_tx_model(address)
                _transaction_info = TransactionInfo()
                _address_info_match.append(_transaction_info)
                _transaction_info.hash = tx_info['hash']
                _transaction_info.address = address
                session.add(_transaction_info)
            session.commit()
            return True
        except:
            session.rollback()
            raise


def get_address_info(address, page=1, since_id=0, size=10):
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _address_info = session.query(AddressInfo).filter(AddressInfo.address == address).first()
        if _address_info is None:
            return None
        _address_info = model_to_dict(_address_info)
        TransactionInfo = gen_address_tx_model(address)
        _address_info['tx'] = []
        filters = [TransactionInfo.address == address]
        if since_id:
            filters.append(TransactionInfo.id < since_id)
            offset = 0
        else:
            offset = (page - 1) * size
        for _transaction_info in session.query(TransactionInfo) \
                                        .filter(*filters) \
                                        .order_by(TransactionInfo.id.desc()) \
                                        .limit(size) \
                                        .offset(offset):
            _address_info['tx'].append(model_to_dict(_transaction_info))
        return _address_info

