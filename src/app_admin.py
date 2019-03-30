#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import os
import time
import traceback

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from flask import Flask, g, request, jsonify, session, render_template, \
    flash, redirect, url_for
import form
import rest_log

from v8.engine.handlers.node_handler import get_all_node, get_node_distribution, \
    get_block_status
from v8.config import config, config_online
config.from_object(config_online)  # noqa

from config import REST_BLOCK_STATUS_KYE_NODE_IP_TYPE
from config import PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT

rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))

app = Flask(__name__)
app.secret_key = 'green rseading key'
app.config['SESSION_TYPE'] = 'filesystem'


@app.route('/lbtc/explorer', methods=['GET'])
def lbtc_index():
    lbtc_info = {}
    new_block = []
    rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
    time_now = datetime.datetime.now()
    block_status = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)
    if not block_status:
        flash(u'区块高度错误', 'error')
        return render_template('index.html', lbtc_info=lbtc_info)
    previous_block_hash = ''
    current_height = block_status['height']
    best_height_time = 0
    try:
        for i in range(0, 10):
            block_info = {}
            if not previous_block_hash:
                previous_block_hash = rpc_connection.getblockhash(current_height)
            block = rpc_connection.getblock(previous_block_hash)
            if not block:
                flash(u'区块高度错误', 'error')
                return render_template('index.html', lbtc_info=lbtc_info)
            previous_block_hash = block['previousblockhash']
            block_info['miner'] = 'miner name'
            block_info['award'] = '0.0625'
            block_info['height'] = '{:,}'.format(block['height'])
            block_info['size'] = '{:,}'.format(block['strippedsize'])
            time_delta = (time_now - datetime.datetime.fromtimestamp(block['time'])).seconds
            if not best_height_time: best_height_time = block['time'] + 1
            if time_delta < 3:
                block_info['time'] = str(time_delta) + u'秒钟前'
            else:
                block_info['time'] = str(best_height_time - block['time']) + u'秒钟前'
            for key in ['previousblockhash', 'hash']:
                block_info[key] = block[key]
            new_block.append(block_info)

        lbtc_info['unconfirmed_tx_num'] = rpc_connection.getmempoolinfo()['size']
    except Exception as e:
        print(unicode(e))
    lbtc_info['block_info'] = new_block
    lbtc_info['delegate_count'] = 0
    lbtc_info['active_delegate_count'] = 0
    lbtc_info['delegate_area'] = 0
    lbtc_info['address_count'] = 0
    lbtc_info['average_tx_speed'] = 0
    lbtc_info['tx_count'] = 0
    lbtc_info['average_tx_cost'] = 0
    lbtc_info['average_block_size'] = 0

    node_status = get_block_status(REST_BLOCK_STATUS_KYE_NODE_IP_TYPE)
    lbtc_info['delegate_count'] = node_status['node_num']
    node_distribution = get_node_distribution(7)
    for _distribution in node_distribution:
        _distribution['node_num'] = str(_distribution['node_num']) + ' ({0:.2f}%)'.format(_distribution['node_persent'])
    lbtc_info['node_distribution'] = node_distribution
    return render_template('index.html', lbtc_info=lbtc_info)


@app.route('/lbtc/get_block', methods=['GET'])
def lbtc_block():
    block_hash = request.args.get('hash', None)
    height = None
    if not block_hash:
        height = int(request.args.get('height', '0').replace(',', ''))
        if not height:
            flash(u'区块Hash或高度错误', 'error')
            return redirect(url_for('lbtc_index'))
    rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
    try:
        if height:
            block_hash = rpc_connection.getblockhash(height)
        if not block_hash:
            flash(u'区块Hash或高度错误', 'error')
            return redirect(url_for('lbtc_index'))
        _info_block = rpc_connection.getblock(block_hash)
    except Exception as e:
        flash(u'区块Hash或高度错误', 'error')
        return redirect(url_for('lbtc_index'))
    
    tx_info = [{'income': '0.1',
                'hash': '05b0f61ac567d35ed0a143a596a308685812d729762b039e9f849304183c7da3',
                'height': 1000,
                'size': 10,
                'confirm_num': 110,
                'time': '2019-03-28 16:12:16',
                'lbtc_input': '0.11',
                'lbtc_output': '0.1',
                'fee': '0.01',
                'input_num': 1,
                'output_num': 1,
                'input_tx': [{'address': 'qrm82nh4heasz84ga3wc88pnl4saj50pru592c46vm', 'amount': '0.11'}],
                'output_tx': [{'address': 'pz3t0g8699xrn65q6cdfel867svgc35ql5pvwhunse', 'amount': '0.10'}],},
               {'income': '-0.1',
                'hash': '05b0f61ac567d35ed0a143a596a308685812d729762b039e9f849304183c7da3',
                'height': 1000,
                'size': 10,
                'confirm_num': 110,
                'time': '2019-03-28 16:12:16',
                'lbtc_input': '0.11',
                'lbtc_output': '0.1',
                'fee': '0.01',
                'input_num': 1,
                'output_num': 1,
                'input_tx': [{'address': 'qrm82nh4heasz84ga3wc88pnl4saj50pru592c46vm', 'amount': '0.11'}],
                'output_tx': [{'address': 'pz3t0g8699xrn65q6cdfel867svgc35ql5pvwhunse', 'amount': '0.10'}],
               }]

    block_info = {'tx_info': tx_info}
    for key in ['merkleroot', 'nonce', 'previousblockhash', 'hash', 'height', 'confirmations',
                'time', 'versionHex', 'strippedsize', 'tx']:
        block_info[key] = _info_block[key]
    block_info['time'] = datetime.datetime.fromtimestamp(block_info['time']).strftime('%Y-%m-%d %H:%M:%S')
    block_info['transaction_num'] = len(_info_block['tx'])
    block_info['miner_name'] = 'miner_name'
    block_info['next_hash'] = ''
    block_info['height'] = '{:,}'.format(block_info['height'])
    return render_template('block.html', block_info=block_info, show_tx_hash=True, float=float)


@app.route('/lbtc/pool', methods=['GET'])
def lbtc_pool():
    lbtc_info = {}
    return render_template('index.html', lbtc_info=lbtc_info)


@app.route('/lbtc/search', methods=['GET'])
def lbtc_search():
    lbtc_info = {}
    return render_template('index.html', lbtc_info=lbtc_info)


@app.route('/lbtc/balance', methods=['GET'])
def lbtc_balance():
    lbtc_info = {}
    return render_template('index.html', lbtc_info=lbtc_info)


@app.route('/lbtc/address', methods=['GET'])
def lbtc_address():
    address = request.args.get('address', '')
    if not address:
        flash(u'钱包地址错误', 'error')
        return redirect(url_for('lbtc_index'))
    tx_info = [{'income': '0.1',
                'hash': '05b0f61ac567d35ed0a143a596a308685812d729762b039e9f849304183c7da3',
                'height': 1000,
                'size': 10,
                'confirm_num': 110,
                'time': '2019-03-28 16:12:16',
                'lbtc_input': '0.11',
                'lbtc_output': '0.1',
                'fee': '0.01',
                'input_num': 1,
                'output_num': 1,
                'input_tx': [{'address': 'qrm82nh4heasz84ga3wc88pnl4saj50pru592c46vm', 'amount': '0.11'}],
                'output_tx': [{'address': 'pz3t0g8699xrn65q6cdfel867svgc35ql5pvwhunse', 'amount': '0.10'}],},
               {'income': '-0.1',
                'hash': '05b0f61ac567d35ed0a143a596a308685812d729762b039e9f849304183c7da3',
                'height': 1000,
                'size': 10,
                'confirm_num': 110,
                'time': '2019-03-28 16:12:16',
                'lbtc_input': '0.11',
                'lbtc_output': '0.1',
                'fee': '0.01',
                'input_num': 1,
                'output_num': 1,
                'input_tx': [{'address': 'qrm82nh4heasz84ga3wc88pnl4saj50pru592c46vm', 'amount': '0.11'}],
                'output_tx': [{'address': 'pz3t0g8699xrn65q6cdfel867svgc35ql5pvwhunse', 'amount': '0.10'}],
               }]
    address_info = {'address': address,
                    'balance': '0.1',
                    'transaction_num': 2,
                    'create_time': '2019-03-28 16:12:16',
                    'tx_info': tx_info}
    return render_template('address.html', address_info=address_info, not_href_address=address,
                           show_income=True, show_tx_hash=True, show_tx_height=True, float=float)


@app.route('/lbtc/tx', methods=['GET'])
def lbtc_tx():
    tx_hash = request.args.get('hash', '')
    if not tx_hash:
        flash(u'交易hash错误', 'error')
        return redirect(url_for('lbtc_index'))
    tx_info = {'hash': tx_hash,
               'height': 1000,
               'size': 10,
               'confirm_num': 110,
               'time': '2019-03-28 16:12:16',
               'lbtc_input': '0.11',
               'lbtc_output': '0.1',
               'fee': '0.01',
               'input_num': 1,
               'output_num': 1,
               'input_tx': [{'address': 'qrm82nh4heasz84ga3wc88pnl4saj50pru592c46vm', 'amount': '0.11'}],
               'output_tx': [{'address': 'pz3t0g8699xrn65q6cdfel867svgc35ql5pvwhunse', 'amount': '0.10'}],
    }
    return render_template('tx.html', tx_info=tx_info, show_income=False, show_tx_height=True)


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

@app.route('/lbtc/nodes', methods=['GET'])
def lbtc_nodes():
    node_distribution = get_node_distribution(10)
    for _distribution in node_distribution:
        _distribution['node_num'] = str(_distribution['node_num']) + \
                                    ' ({0:.2f}%)'.format(_distribution['node_persent'])
    node_status = get_block_status(REST_BLOCK_STATUS_KYE_NODE_IP_TYPE)

    country = request.args.get('country', '')
    valid_node = get_all_node(2, country=country)
    if not country: country = u'所有地区节点列表'
    else: country += u' 节点列表'
    '''
    valid_node = []
    for _node in all_node:
        if _node['ip'].endswith(':9333'):
            valid_node.append(_node)
    '''
    #valid_node = sorted(all_node, cmp=node_cmp)
    count = 1
    for _node in valid_node:
        _node['id'] = count
        count += 1
    return render_template('node.html', all_node=valid_node, country=country,
                           node_distribution=node_distribution, node_status=node_status)
        

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
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5025)
