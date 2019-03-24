#!/usr/bin/python
# -*- coding: utf-8 -*-

import contextlib
import datetime

from v8.engine import db_conn
from v8.model.user import User
from v8.engine.util import model_to_dict


def get_user_info(email_address):
    """Get user info by email_address.

    Args:
        email_address (string): user's email address

    Returns:
        dict of user info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _user = session.query(User) \
                       .filter(User.deleted == 0,
                               User.email_address == email_address) \
                       .first()
        if not _user:
            return None
        else:
            return model_to_dict(_user)


def get_all_user_info():
    """Get all user info.

    Args:

    Returns:
        list of user info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        ret = []
        for _user in session.query(User).filter(User.deleted == 0) \
                                        .order_by(User.id):
            ret.append(model_to_dict(_user))
        return ret


def delete_user_with_email_address(email_address):
    """Delete user info by email_address.

    Args:
        email_address (string): user's email address

    Returns:
        dict of user info or None.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _user = session.query(User) \
                       .filter(User.deleted == 0,
                               User.email_address == email_address) \
                       .first()
        if not _user:
            return None
        else:
            _user.deleted = 1
            session.commit()
            return model_to_dict(_user)


def add_or_update_user_admin(email_address, password, is_admin, device_type_ids):
    """Add or update a user.

    Args:

    Returns:
        dict of user info.
    """
    with contextlib.closing(db_conn.gen_session_class('base')()) as session:
        _user = session.query(User) \
                       .filter(User.deleted == 0,
                               User.email_address == email_address) \
                       .first()
        if _user:
            _user.email_address = email_address,
            _user.password = password
            _user.is_admin = is_admin
            _user.device_type_ids = device_type_ids
            _user.update_time = datetime.datetime.now()
            session.commit()
            return model_to_dict(_user)
        else:
            _user = User()
            _user.email_address = email_address,
            _user.password = password
            _user.deleted = 0
            _user.is_admin = is_admin
            _user.device_type_ids = device_type_ids
            _user.create_time = datetime.datetime.now()
            _user.update_time = _user.create_time
            session.add(_user)
            session.commit()
            return model_to_dict(_user)
