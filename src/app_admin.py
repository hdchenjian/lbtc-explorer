#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import os
import time
import traceback

from flask import Flask, g, request, jsonify, session, render_template, \
    flash, redirect, url_for

from v8.engine.handlers.node_handler import get_all_node, add_node, update_node

from config import V8_CONFIG, DEBUG
from v8.config import config
config.from_object(V8_CONFIG)  # noqa
import form
import rest_log

app = Flask(__name__)
app.secret_key = 'green rseading key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route("/")
def index():
    return redirect(url_for("nodes"))



@app.route('/nodes', methods=["GET"])
def nodes():
    all_node = get_all_node()
    count = 1
    for _node in all_node:
        _node['id'] = count
        count += 1
    return render_template("index.html", all_node=all_node)
        

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
    app.run(host='0.0.0.0', port=5025, debug=DEBUG)
