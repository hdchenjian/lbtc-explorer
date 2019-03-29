#!/usr/bin/python3
# -*- coding: utf-8 -*-

import fcntl
import functools
import os
import sys
import traceback

from flask import g, flash, redirect, url_for


def singleton(pid_filename):
    def decorator(f):
        @functools.wraps(f)
        def decorated(*args, **kwargs):
            pid = str(os.getpid())
            pidfile = open(pid_filename, 'a+')
            try:
                fcntl.flock(pidfile.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                return
            pidfile.seek(0)
            pidfile.truncate()
            pidfile.write(pid)
            pidfile.flush()
            pidfile.seek(0)

            ret = f(*args, **kwargs)

            try:
                pidfile.close()
            except IOError as err:
                if err.errno != 9:
                    return
            os.remove(pid_filename)
            return ret
        return decorated
    return decorator


def log_request(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        g.log_info['func_name'] = f.func_name
        g.log_info['args'] = [str(a) for a in args]
        g.log_info['pid'] = os.getpid()
        if kwargs:
            g.log_info['kwargs'] = kwargs
        try:
            ret = f(*args, **kwargs)
            g.log_info['ret'] = ret.response
        except:
            e = sys.exc_info()[0]
            g.log_info['exception'] = str(e)
            g.log_info['format_exc'] = traceback.format_exc()
            g.log_info['ret'] = str(e)
            raise
        return ret
    return decorated


def verify_logined(app):
    @app.before_request
    def login_required():
        if not(hasattr(g, 'logined') and g.logined is True):
            flash(u'请先登录', 'warning')
            return redirect(url_for("user_login"))
    return app
