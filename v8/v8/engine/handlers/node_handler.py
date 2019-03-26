#!/usr/bin/python
# -*- coding: utf-8 -*-

import contextlib
import datetime

from sqlalchemy.sql import func

from v8.engine import db_conn
from v8.model.lbtc_node import LbtcNode, NodeNotValid
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


def get_all_node(node_status, deleted_node=1):
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
                _node.location = ''
                _node.network = ''
                _node.height = 0
                _node.pix = 0
                _node.latitude = 0
                _node.longitude = 0
                _node.status = 1
                _node.deleted = 0
                _node.create_time = time_now
                session.add(_node)
            for _key in ['user_agent', 'location', 'network', 'height', 'pix', 'status', 'deleted',
                         'latitude', 'longitude']:
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
