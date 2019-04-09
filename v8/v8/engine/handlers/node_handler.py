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
        except Exception:
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
                _node.status = 0
                _node.deleted = 0
                _node.create_time = time_now
                session.add(_node)
            for _key in ['user_agent', 'services', 'location', 'timezone', 'network', 'asn',
                         'height', 'pix', 'status', 'deleted', 'latitude', 'longitude']:
                if _key in node_info:
                    setattr(_node, _key, node_info[_key])
            _node.update_time = time_now
            session.commit()
        except Exception:
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
        except Exception:
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
            return count
        except Exception:
            session.rollback()
            return None


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
                            .order_by(NodeDistribution.rank) \
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
    if not country_info:
        return False
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        for _node in session.query(NodeDistribution) \
                            .filter(~NodeDistribution.country.in_(country_info.keys())):
            _node.deleted = 1
            session.commit()
        try:
            for country_name in country_info:
                _country = session.query(NodeDistribution) \
                                  .filter(NodeDistribution.country == country_name) \
                                  .first()
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
        except Exception:
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
        except Exception:
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


def delete_many_tx(tx_ids):
    """Delete many tx.

    Args:
        txs (list): list of tx

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    result = conn.lbtc.lbtc_tx.delete_many({'_id': {'$in': tx_ids}})
    return result.deleted_count


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
    for doc in conn.lbtc.lbtc_tx.find({'_id': {'$in': txs}, 'input': ['coinbase', '']}):
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


def find_many_tx(tx_ids, sort=False):
    """Find one tx.

    Args:
        tx_ids (list):

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    result = []
    if sort:
        for doc in conn.lbtc.lbtc_tx.find(
                {'_id': {'$in': tx_ids}}).sort("height", pymongo.DESCENDING):
            result.append(doc)
    else:
        doc_limit = 86400
        if len(tx_ids) > doc_limit:
            find_times = len(tx_ids) // doc_limit + 1
            for i in range(0, find_times):
                print("BSON document too large", len(tx_ids), i, i*doc_limit, (i+1)*doc_limit)
                for doc in conn.lbtc.lbtc_tx.find(
                        {'_id': {'$in': tx_ids[i*doc_limit: (i+1)*doc_limit]}}):
                    result.append(doc)
        else:
            for doc in conn.lbtc.lbtc_tx.find(
                    {'_id': {'$in': tx_ids}}):
                result.append(doc)
    return result


def update_many_delegate_active(delegate_ids):
    """Add one delegate.

    Args:
        tx (dict): dict of delegate

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    conn.lbtc.lbtc_delegate.update_many(
        {'_id': {'$in': delegate_ids}}, {'$set': {'active': True}}, upsert=False)


def update_all_committee(all_committee):
    """Add all committee.

    Args:
        tx (list): list of committee

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    for _committee in all_committee:
        conn.lbtc.lbtc_committee.update_one(
            {'_id': _committee['address']}, {'$set': _committee}, upsert=True)


def update_all_proposal(all_proposal):
    """Add all proposal.

    Args:
        tx (list): list of proposal

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    for _proposal in all_proposal:
        conn.lbtc.lbtc_proposal.update_one(
            {'_id': _proposal['id']}, {'$set': _proposal}, upsert=True)


def update_all_delegate(all_delegate):
    """Add one delegate.

    Args:
        tx (dict): dict of delegate

    Returns:

    """
    conn = db_conn.gen_mongo_connection('base')
    for _delegate in all_delegate:
        conn.lbtc.lbtc_delegate.update_one(
            {'_id': _delegate['_id']}, {'$set': _delegate}, upsert=True)


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


def query_all_proposal(bill_id=''):
    """Add all proposal.

    Args:

    Returns:
        tx (list): list of proposal

    """
    conn = db_conn.gen_mongo_connection('base')
    if bill_id:
        _proposal = conn.lbtc.lbtc_proposal.find_one({'_id': bill_id})
        return _proposal
    else:
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
    ret = [{'_id': '166D9UoFdPcDEGFngswE226zigS8uBnm3C',
            'index': 1,
            'funds': '0', 'votes': '21000000', 'name': 'LBTCSuperNode', 'active': False}]
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
        except Exception:
            session.rollback()
            raise


def delete_block_info(height):
    """Delete a node.

    Args:

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        count = 0
        try:
            count = session.query(BlockInfo).filter(BlockInfo.height == height).delete()
            session.commit()
            return count
        except Exception:
            session.rollback()
            raise


def update_address_info(address, amount, time):
    """Add a node.

    Args:

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        try:
            _address_info = \
                session.query(AddressInfo).filter(AddressInfo.address == address).first()
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
            _address_info.update_time = time
            session.commit()
            return True
        except Exception:
            session.rollback()
            raise


def update_many_address_info(address_list, key, current_height_info):
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
                _address_info = \
                    session.query(AddressInfo).filter(AddressInfo.address == address).first()
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
                _address_info.update_time = time

                TransactionInfo = gen_address_tx_model(address)
                _transaction_info = TransactionInfo()
                _address_info_match.append(_transaction_info)
                _transaction_info.hash = tx_info['hash']
                _transaction_info.address = address
                session.add(_transaction_info)
            time_now = datetime.datetime.now()
            _block_status = session.query(BlockStatus).filter(BlockStatus.key == key).first()
            if _block_status is None:
                _block_status = BlockStatus()
                _block_status.key = key
                _block_status.create_time = time_now
                session.add(_block_status)
            _block_status.update_time = time_now
            _block_status.value = json.dumps(current_height_info)
            session.commit()
            return True
        except Exception:
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


def update_network_tx_statistics(key, network_tx_statistics):
    time_now = datetime.datetime.now()
    time_yesterday = time_now - datetime.timedelta(days=1)
    time_14d_ago = time_now - datetime.timedelta(days=14)
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        network_tx_statistics['address_num'] = session.query(AddressInfo).count()
        network_tx_statistics['address_num_24h'] = \
            session.query(AddressInfo) \
                   .filter(AddressInfo.create_time > time_yesterday) \
                   .count()
        network_tx_statistics['address_num_14d'] = \
            session.query(AddressInfo) \
                   .filter(AddressInfo.create_time > time_14d_ago) \
                   .count()
        update_block_status(key, network_tx_statistics)


def update_most_rich_address(key, top=100):
    address_ids = []
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        for _address_info in session.query(AddressInfo) \
                                    .order_by(AddressInfo.balance.desc()) \
                                    .limit(top):
            address_ids.append(_address_info.id)
    update_block_status(key, address_ids)


def query_most_rich_address(key, key_utxo):
    ret = []
    key_value = get_block_status_multi_key([key, key_utxo])
    if not key_value[key]:
        return ret
    total_amount = float(key_value[key_utxo]['total_amount'])
    rank = 1
    sum_balance = Decimal(0)
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        for _address_info in session.query(AddressInfo) \
                                    .filter(AddressInfo.id.in_(key_value[key])) \
                                    .order_by(AddressInfo.balance.desc()):
            _address_info_dict = model_to_dict(_address_info)
            _address_info_dict['persent'] = \
                "{0:.2f} %".format(float(_address_info_dict['balance']) / total_amount * 100)
            sum_balance += Decimal(_address_info_dict['balance'])
            _address_info_dict['sum_persent'] = \
                "{0:.2f} %".format(float(sum_balance) / total_amount * 100)
            _address_info_dict['balance'] = \
                str(_address_info_dict['balance']).rstrip('0').rstrip('.')
            _address_info_dict['rank'] = rank
            rank += 1
            ret.append(_address_info_dict)
        return ret


def query_address_info(address):
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _address_info = session.query(AddressInfo).filter(AddressInfo.address == address).first()
        if _address_info:
            return model_to_dict(_address_info)
        else:
            return None


def update_address_info_update_time():
    address_to_update_time = {}
    tx_ids = []
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        for _address_info in session.query(AddressInfo):
            TransactionInfo = gen_address_tx_model(_address_info.address)
            _transaction_info = session.query(TransactionInfo) \
                                       .filter(TransactionInfo.address == _address_info.address) \
                                       .order_by(TransactionInfo.id.desc()).first()
            tx_ids.append(_transaction_info.hash)
        _tx_list = find_many_tx(tx_ids)
        for _tx_item in _tx_list:
            for i in range(0, len(_tx_item['input']) // 2):
                if _tx_item['input'][0] == 'coinbase':
                    continue
                if _tx_item['input'][2*i] not in address_to_update_time:
                    address_to_update_time[_tx_item['input'][2*i]] = _tx_item['time']
                elif _tx_item['time'] > address_to_update_time[_tx_item['input'][2*i]]:
                    address_to_update_time[_tx_item['input'][2*i]] = _tx_item['time']
            for i in range(0, len(_tx_item['output']) // 3):
                if _tx_item['output'][3*i + 1] == 'nulldata':
                    continue
                if _tx_item['output'][3*i + 1] not in address_to_update_time:
                    address_to_update_time[_tx_item['output'][3*i + 1]] = _tx_item['time']
                elif _tx_item['time'] > address_to_update_time[_tx_item['output'][3*i + 1]]:
                    address_to_update_time[_tx_item['output'][3*i + 1]] = _tx_item['time']

        for _address in address_to_update_time:
            _address_info = \
                session.query(AddressInfo).filter(AddressInfo.address == _address).first()
            _address_info.update_time = address_to_update_time[_address]
        session.commit()


def update_address_growth_daily_info():
    all_address_growth_daily = []
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        address_latest = session.query(AddressInfo) \
                                .order_by(AddressInfo.id.desc()).first()
        if not address_latest:
            return
        end_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        address_growth_daily_latest = session.query(AddressGrowthDaily) \
                                             .order_by(AddressGrowthDaily.time.desc()).first()
        if not address_growth_daily_latest:
            start_time = datetime.datetime.strptime('2018-10-11 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            start_time = address_growth_daily_latest.time
            start_time = datetime.datetime(start_time.year, start_time.month, start_time.day) + \
                datetime.timedelta(days=2)
        while(start_time <= end_time):
            address_total = session.query(AddressInfo) \
                                   .filter(AddressInfo.create_time < start_time).count()
            address_count = session.query(AddressInfo) \
                                   .filter(AddressInfo.create_time < start_time,
                                           AddressInfo.create_time >=
                                           (start_time - datetime.timedelta(days=1))).count()
            _address_growth_daily = AddressGrowthDaily()
            all_address_growth_daily.append(_address_growth_daily)
            session.add(_address_growth_daily)
            _address_growth_daily.total_address = address_total
            _address_growth_daily.increase_address = address_count
            _address_growth_daily.time = (start_time - datetime.timedelta(days=1)).date()
            start_time += datetime.timedelta(days=1)
        try:
            session.commit()
            return len(all_address_growth_daily)
        except Exception:
            session.rollback()
            return None


def update_transaction_daily_info():
    all_transaction_daily = []
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        block_info_latest = session.query(BlockInfo) \
                                   .order_by(BlockInfo.height.desc()).first()
        if not block_info_latest:
            return
        end_time = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        transaction_daily_latest = session.query(TransactionDaily) \
                                          .order_by(TransactionDaily.time.desc()).first()
        if not transaction_daily_latest:
            start_time = datetime.datetime.strptime('2018-10-11 00:00:00', '%Y-%m-%d %H:%M:%S')
        else:
            start_time = transaction_daily_latest.time
            start_time = datetime.datetime(start_time.year, start_time.month, start_time.day) + \
                datetime.timedelta(days=2)

        while(start_time <= end_time):
            total_block_count = 0
            total_block_size = 0
            tx_num = 0
            for _block_info in session.query(BlockInfo) \
                                      .filter(BlockInfo.create_time < start_time,
                                              BlockInfo.create_time >=
                                              (start_time - datetime.timedelta(days=1))):
                total_block_count += 1
                total_block_size += _block_info.strippedsize
                tx_num += _block_info.tx_num
            _transaction_daily = TransactionDaily()
            session.add(_transaction_daily)
            all_transaction_daily.append(_transaction_daily)
            _transaction_daily.total_block_count = total_block_count
            _transaction_daily.tx_num = tx_num
            _transaction_daily.tx_num_no_coinbase = tx_num - total_block_count
            _transaction_daily.avg_block_size = float(total_block_size) / float(total_block_count)
            _transaction_daily.time = (start_time - datetime.timedelta(days=1)).date()
            start_time += datetime.timedelta(days=1)
        try:
            session.commit()
            return len(all_transaction_daily)
        except Exception:
            session.rollback()
            return None


def query_transaction_daily_info():
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _transaction_daily in session.query(TransactionDaily).order_by(TransactionDaily.id):
            ret.append(model_to_dict(_transaction_daily))
        return ret


def query_address_daily_info():
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _address_daily in session.query(AddressGrowthDaily).order_by(AddressGrowthDaily.id):
            ret.append(model_to_dict(_address_daily))
        return ret
