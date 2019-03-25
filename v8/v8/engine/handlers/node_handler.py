#!/usr/bin/python
# -*- coding: utf-8 -*-

import contextlib
import datetime

from sqlalchemy.sql import func

from v8.engine import db_conn
from v8.model.lbtc_node import LbtcNode
from v8.engine.util import model_to_dict


def get_all_node():
    """Get node info.

    Args:

    Returns:
        list of node or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _node in session.query(LbtcNode) \
                            .filter(LbtcNode.deleted == 0) \
                            .order_by(LbtcNode.height.desc()):
            ret.append(model_to_dict(_node))
        return ret

        
def add_or_update_node(ip, user_agent, location, network, height, pix, status):
    """Add a node, update a node when node exist.

    Args:
        ip (string): ip and port, for example: 120.78.147.20:9333
        user_agent (string): client version
        location (string): host location
        network (string): network status
        height (int): block height
        pix (float): calculated properties and network metrics every 24 hours
        status (int): 0: offline, 1: online

    Returns:
        dict of node info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _node = session.query(LbtcNode).filter(LbtcNode.ip == ip).first()
        time_now = datetime.datetime.now()
        try:
            if not _node:
                _node = LbtcNode()
                _node.ip = ip
                _node.create_time = time_now
                session.add(_node)
                _node.deleted = 0
            _node.user_agent = user_agent
            _node.location = location
            _node.network = network
            _node.height = height
            _node.pix = pix
            _node.status = status
            _node.update_time = time_now
            session.commit()
        except:
            session.rollback()
            raise
        return model_to_dict(_node)


def update_node(ip, node_info):
    """Update node info.

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
        _node = session.query(LbtcNode).filter(LbtcNode.ip == ip).first()
        if _node is None:
            return None
        for _key in ['user_agent', 'location', 'network', 'height', 'pix', 'status', 'deleted']:
            if _key in node_info:
                setattr(_node, _key, node_info[_key])
        _node.update_time = datetime.datetime.now()
        session.commit()
        return model_to_dict(_node)
