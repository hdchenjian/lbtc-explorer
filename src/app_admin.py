#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import time
import traceback

from flask import Flask, g, request, jsonify, session, render_template, \
    flash, redirect, url_for

from v8.engine.handlers.node_handler import get_all_node

from config import V8_CONFIG
from v8.config import config
config.from_object(V8_CONFIG)  # noqa
import form
import rest_log

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))

app = Flask(__name__)
app.secret_key = 'green rseading key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/lbtc/")
def index():
    return redirect(url_for("lbtc_block"))


@app.route('/lbtc/block', methods=["GET"])
def lbtc_block():
    block_info = {}
    return render_template("block.html", block_info=block_info)


@app.route('/lbtc/search', methods=["GET"])
def lbtc_search():
    block_info = {}
    return render_template("block.html", block_info=block_info)


def node_cmp(a, b):
    if a['height'] > b['height']:
        return -1
    elif a['height'] == b['height']:
        port_a = int(a['ip'].split(':')[1])
        port_b = int(b['ip'].split(':')[1])
        if port_a == 9333:
            return -1
        elif port_b == 9333:
            return 1
        else:
            return 0
    else:
        return 1

@app.route('/lbtc/nodes', methods=["GET"])
def nodes():
    all_node = get_all_node(2)
    '''
    valid_node = []
    for _node in all_node:
        if _node['ip'].endswith(':9333'):
            valid_node.append(_node)
    '''
    valid_node = sorted(all_node, cmp=node_cmp)
    count = 1
    for _node in valid_node:
        if '|' in _node['user_agent']:
            _node['user_agent'], _node['services'] = _node['user_agent'].split('|')
        else:
            _node['services'] = ''
        if '|' in _node['location']:
            _node['location'], _node['timezone'] = _node['location'].split('|')
        else:
            _node['timezone'] = ''
        if '|' in _node['network']:
            _node['network'], _node['asn'] = _node['network'].split('|')
        else:
            _node['asn'] = ''
        _node['id'] = count
        count += 1
    return render_template("index.html", all_node=valid_node)
        

@app.before_request
def before_request():
    g.log_info = dict()
    if 'X-Real-IP' in request.headers:
        g.log_info['remote_addr'] = request.headers['X-Real-IP']
        g.remote_addr = request.headers['X-Real-IP']
    else:
        g.log_info['remote_addr'] = request.headers.get('X-Forwarded-For')
        g.remote_addr = request.headers.get('X-Forwarded-For')
    if not g.remote_addr:
        g.remote_addr = request.remote_addr
    g.log_info['request_data'] = request.data
    g.log_info['method'] = request.method
    g.log_info['url'] = request.url
    g.log_info['headers'] = dict(request.headers)
    g.log_info['form'] = dict(request.form)
    g.log_info['start_time'] = time.time()


@app.after_request
def after_request(response):
    g.log_info['end_time'] = time.time()
    g.log_info['process_time'] = \
        g.log_info['end_time'] - g.log_info['start_time']

    g.log_info['status_code'] = response.status_code
    g.log_info['ret_headers'] = dict(response.headers)

    if 400 <= response.status_code < 500:
        rest_log.logger.warning(g.log_info)
    else:
        rest_log.logger.info(g.log_info)

    response.headers['Date'] = \
        datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    return response


@app.errorhandler(404)
def uri_not_found(exception):
    ret = dict()
    ret['code'] = 1000
    ret['error'] = 'uri_not_found'
    ret['request'] = ' '.join([request.method, request.url])
    return jsonify(ret), 404


@app.errorhandler(500)
def internal_server_error(exception):
    ret = dict()
    ret['code'] = 999
    ret['error'] = 'unknown_error'
    ret['request'] = ' '.join([request.method, request.url])
    ret['exception'] = str(exception)
    ret['detail'] = u'服务器维护中'
    return jsonify(ret), 500


@app.teardown_request
def teardown_request(exception):
    if getattr(g, 'log_info', None) is None:
        g.log_info = dict()

    if exception:
        g.log_info['exception'] = str(exception)
        g.log_info['format_exc'] = traceback.format_exc()
        rest_log.logger.critical(g.log_info)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025, debug=False)
