#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import time
import traceback
from decimal import Decimal
import re
import pprint
import json

from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

from flask import Flask, g, request, jsonify, render_template, \
    flash, redirect, url_for, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import rest_log

from v8.engine.handlers.node_handler import get_all_node, get_node_distribution, \
    get_block_status, get_block_status_multi_key, query_all_committee, query_all_delegate, \
    query_all_proposal, query_coinbase_tx, find_many_tx, find_one_tx, get_address_info, \
    query_most_rich_address, query_address_info, query_transaction_daily_info, \
    query_address_daily_info, get_block_during, get_balance_distribution
from v8.config import config, config_online

from config import REST_BLOCK_STATUS_KYE_NODE_IP_TYPE, \
    REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME, PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT, \
    REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST, REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO, \
    REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME, \
    REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS, \
    REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS, REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS, \
    REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE


config.from_object(config_online)

app = Flask(__name__)
app.secret_key = 'green rseading key'
app.config['SESSION_TYPE'] = 'filesystem'
limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["2000/day; 500/hour; 40/minute"])


address_daily_info_global = None
transaction_daily_info_global = None
transaction_daily_info_global_update_time = None

delegate_count_global = 0
normal_count_global = 0
stop_count_global = 0
delegate_info_global = []
delegate_info_global_update_time = None

all_rpc_function = []

address_to_no_mongo_tx = {}
memcache_block_height = 0
memcache_reset_time = 0

address_to_remark = {'1F3mbWEw32ove5FvogXJkLExCRszuUQnDF': 'richest',
                     '1DZCJu71LZtftX1njhhZeCL1v8xgKdKXnv': 'cobo',
                     '13ZWkQNxaLCuEoHBmLHju4hVqEs3kgZJca': 'zb',
                     '115pmmN6tgxPkQ4RiyiM5F2VB4gy1uHfeW': 'mxc'
}

@app.route('/lbtc/rpc', methods=['GET'])
def lbtc_rpc():
    cmd = request.args.get('cmd', '')
    run = int(request.args.get('run', '0'))
    result = 'default_string_doc'
    global all_rpc_function
    if not all_rpc_function:
        rpc_connection_local = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
        all_function_str = rpc_connection_local.help()
        all_function_str = all_function_str.split('\n')

        all_rpc_function_local = []
        for _function in all_function_str:
            if not _function:
                continue
            if '== ' in _function:
                continue
            if ' ' not in _function:
                _function_name = _function
            else:
                _function_name = _function.split(' ')[0]
            all_rpc_function_local.append(_function_name)
        all_rpc_function = all_rpc_function_local

    if cmd and cmd not in all_rpc_function:
        flash(u'Command not found: ' + cmd , 'error')
        return render_template('rpc/getblock' + '.html')
    if run:
        if cmd in ['getdifficulty', 'pruneblockchain', 'stop', 'disconnectnode', 'setban',
                   'setnetworkactive', 'backupwallet', 'dumpprivkey', 'dumpwallet',
                   'encryptwallet']:
            return render_template('rpc/' + cmd + '.html', result=0)
        if cmd in ['getmempoolancestors', 'getmempooldescendants', 'getmempoolentry']:
            return render_template('rpc/' + cmd + '.html', result=[])

        index = 1
        params = []
        while True:
            param_name = 'param' + str(index)
            if param_name not in request.args:
                break
            if request.args[param_name]:
                params.append(request.args[param_name].strip(' '))
            index += 1
        rpc_connection = AuthServiceProxy("http://%s:%s@127.0.0.1:9332" % ('luyao', 'DONNNN'))
        cmd_help = rpc_connection.help(cmd)
        index_param = 0
        if cmd_help.find('Arguments:') > 0:
            cmd_params = cmd_help[cmd_help.find('Arguments:') + len('Arguments:') : cmd_help.find('Result')]
            cmd_params = cmd_params.split('\n')
            for _param in cmd_params:
                if not _param:
                    continue
                if not re.match('[0-9]\. ', _param):
                    continue
                param_type = _param[_param.find(' (') : _param.find(') ')]
                try:
                    if cmd == 'settxfee':
                        if 'numeric' in param_type and index_param < len(params):
                            params[index_param] = params[index_param]
                    elif cmd == 'createrawtransaction':
                        if index_param < len(params) and index_param < 2:
                            params[index_param] = json.loads(params[index_param])
                        elif index_param < len(params) and params[index_param]:
                            params[index_param] = int(params[index_param])
                    else:
                        if 'numeric' in param_type and index_param < len(params):
                            params[index_param] = int(params[index_param])
                except Exception as e:
                    traceback.print_exc()
                    flash(u'run command failed: the ' + str(index_param + 1) + 'th parameter should a number' , 'error')
                    return render_template('rpc/' + cmd + '.html')
                index_param += 1

        _function = getattr(rpc_connection, cmd)
        if cmd == 'gettxoutproof':
            params[0] = [params[0]]
        if _function:
            try:
                result = _function(*params)
            except Exception as e:
                traceback.print_exc()
                flash(u'run command failed: ' + str(e), 'error')
                return render_template('rpc/' + cmd + '.html')
            result = pprint.pformat(result)
        return render_template('rpc/' + cmd + '.html', result=result)
    if not cmd:
        return render_template('rpc/getblock' + '.html')
    else:
        return render_template('rpc/' + cmd + '.html', result=result)


@app.route('/lbtc/explorer', methods=['GET'])
def lbtc_index():
    lbtc_info = {}
    new_block = []
    time_now = datetime.datetime.now()
    key_list = [PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT,
                REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME, REST_BLOCK_STATUS_KYE_NODE_IP_TYPE,
                REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS, REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO]
    block_status_multi_key_value = get_block_status_multi_key(key_list)
    block_status = block_status_multi_key_value[PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT]
    delegate_address_to_name = \
        block_status_multi_key_value[REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME]
    node_status = block_status_multi_key_value[REST_BLOCK_STATUS_KYE_NODE_IP_TYPE]

    previous_block_hash = ''
    current_height = block_status['best_height'] - 3
    irreversible_block_height = block_status['irreversible_block_height']
    best_height_time = 0
    _tx_id_list = []
    rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
    if 'language' in session and session['language'] == 'cn':
        second_suffix = u' 秒钟前'
    else:
        second_suffix = u' seconds ago'
    try:
        for i in range(0, 10):
            block_info = {}
            if not previous_block_hash:
                previous_block_hash = rpc_connection.getblockhash(current_height)
            block = rpc_connection.getblock(previous_block_hash)
            if not block:
                flash(u'区块高度错误', 'error')
                return u'区块高度错误'
            previous_block_hash = block['previousblockhash']
            for _tx_id in block['tx']:
                _tx_id_list.append(_tx_id)
            block_info['tx'] = block['tx']
            block_info['height'] = '{:,}'.format(block['height'])
            block_info['size'] = '{:,}'.format(block['strippedsize'])
            time_delta = \
                int((time_now - datetime.datetime.fromtimestamp(block['time'])).total_seconds())
            if not best_height_time:
                best_height_time = block['time'] + 1
            if time_delta < 3:
                block_info['time'] = str(time_delta) + second_suffix
            else:
                block_info['time'] = str(best_height_time - block['time']) + second_suffix
            for key in ['previousblockhash', 'hash']:
                block_info[key] = block[key]
            new_block.append(block_info)

        lbtc_info['unconfirmed_tx_num'] = rpc_connection.getmempoolinfo()['size']
    except Exception:
        traceback.print_exc()
        flash(u'获取区块数据错误', 'error')
        return u'区块高度错误'

    for _new_block in new_block:
        _new_block['delegate_address'] = ''
        _new_block['award'] = 0
        _new_block['miner'] = ''
        ransactionnew = rpc_connection.gettransactionnew(_new_block['tx'][0])
        if ransactionnew['vout'][0]['scriptPubKey']['type'] == 'pubkeyhash' or \
           ransactionnew['vout'][0]['scriptPubKey']['type'] == 'scripthash':
            if len(ransactionnew['vout'][0]['scriptPubKey']['addresses']) != 1:
                raise ValueError('vout multi addresses')
            current_delegate_address = ransactionnew['vout'][0]['scriptPubKey']['addresses'][0]
            _new_block['delegate_address'] = current_delegate_address
            _new_block['award'] = str(ransactionnew['vout'][0]['value'])
            _new_block['miner'] = delegate_address_to_name[current_delegate_address]

    lbtc_info['block_info'] = new_block

    lbtc_info['delegate_count'] = node_status['node_num']
    node_distribution = get_node_distribution(7)
    for _distribution in node_distribution:
        _distribution['node_num'] = str(
            _distribution['node_num']) + ' ({0:.2f}%)'.format(_distribution['node_persent'])
    lbtc_info['node_distribution'] = node_distribution

    lbtc_info['network_tx_statistics'] = \
        block_status_multi_key_value[REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS]
    total_amount = \
        block_status_multi_key_value[REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO]['total_amount']
    lbtc_info['total_amount'] = total_amount.rstrip('0').rstrip('.')

    global address_daily_info_global
    global transaction_daily_info_global
    global transaction_daily_info_global_update_time
    time_now = datetime.datetime.now()
    if address_daily_info_global is None or \
       (time_now - transaction_daily_info_global_update_time).total_seconds() > 300:
        transaction_daily_info_global = query_transaction_daily_info()
        address_daily_info_global = query_address_daily_info()
        transaction_daily_info_global_update_time = time_now

    tx_daily = {'time': [], 'tx_num': [], 'avg_block_size': [],
                'total_block_count': [], 'tx_num_no_coinbase': []}
    for _daily_info in transaction_daily_info_global:
        tx_daily['time'].append(_daily_info['time'])
        tx_daily['tx_num'].append(_daily_info['tx_num'])
        tx_daily['tx_num_no_coinbase'].append(_daily_info['tx_num_no_coinbase'])
        tx_daily['total_block_count'].append(_daily_info['total_block_count'])
        tx_daily['avg_block_size'].append(str(_daily_info['avg_block_size']))

    address_daily = {'time': [], 'total_address': [], 'increase_address': []}
    for _daily_info in address_daily_info_global:
        address_daily['time'].append(_daily_info['time'])
        address_daily['total_address'].append(_daily_info['total_address'])
        address_daily['increase_address'].append(_daily_info['increase_address'])
    lbtc_info['tx_daily'] = tx_daily
    lbtc_info['address_daily'] = address_daily
    if 'language' in session and session['language'] == 'cn':
        return render_template('cn/index.html', lbtc_info=lbtc_info)
    else:
        return render_template('en/index.html', lbtc_info=lbtc_info)


def get_tx_detail_info(_tx_list, current_height=0, confirmations=None, income_address=''):
    show_address_num = 5
    tx_info = []
    tx_index = 1
    for _tx_item in _tx_list:
        _tx_detail_info = {}
        _tx_detail_info['input_collapse_href'] = '#collapseTxInput' + str(tx_index)
        _tx_detail_info['input_collapse_id'] = 'collapseTxInput' + str(tx_index)
        _tx_detail_info['output_collapse_href'] = '#collapseTxOutput' + str(tx_index)
        _tx_detail_info['output_collapse_id'] = 'collapseTxOutput' + str(tx_index)
        tx_index += 1
        _tx_detail_info['hash'] = _tx_item['_id']
        _tx_detail_info['height'] = _tx_item['height']
        _tx_detail_info['size'] = _tx_item['size']
        if confirmations:
            _tx_detail_info['confirm_num'] = confirmations
        else:
            _tx_detail_info['confirm_num'] = current_height - _tx_item['height']
        _tx_detail_info['time'] = _tx_item['time']
        if income_address:
            _tx_detail_info['income'] = Decimal(0)
        if _tx_item['input'][0] == 'coinbase':
            _tx_detail_info['lbtc_input'] = '0'
            _tx_detail_info['input_tx'] = [{'address': 'CoinBase', 'amount': ''}]
            _tx_detail_info['input_num'] = '0'
        else:
            _tx_detail_info['lbtc_input'] = Decimal(0)
            _tx_detail_info['input_tx'] = []
            for i in range(0, len(_tx_item['input']) // 2):
                _tx_detail_info['lbtc_input'] += Decimal(_tx_item['input'][2*i + 1])
                _tx_detail_info['input_tx'].append(
                    {'address': _tx_item['input'][2*i],
                     'amount': _tx_item['input'][2*i + 1].rstrip('0').rstrip('.')})
                if income_address and income_address == _tx_item['input'][2*i]:
                    _tx_detail_info['income'] -= Decimal(_tx_item['input'][2*i + 1])
            _tx_detail_info['input_num'] = len(_tx_item['input']) // 2
            if len(_tx_detail_info['input_tx']) > show_address_num:
                _tx_detail_info['input_tx_hide'] = _tx_detail_info['input_tx'][show_address_num:]
                _tx_detail_info['input_tx_hide_num'] = len(_tx_detail_info['input_tx_hide'])
                _tx_detail_info['input_tx'] = _tx_detail_info['input_tx'][0:show_address_num]
            else:
                _tx_detail_info['input_tx_hide'] = None

        _tx_detail_info['lbtc_output'] = Decimal(0)
        _tx_detail_info['output_tx'] = []
        _tx_detail_info['output_num'] = 0
        for i in range(0, len(_tx_item['output']) // 3):
            if _tx_item['output'][3*i + 1] == 'nulldata':
                continue
            _tx_detail_info['lbtc_output'] += Decimal(_tx_item['output'][3*i + 2])
            _tx_detail_info['output_tx'].append(
                {'address': _tx_item['output'][3*i + 1],
                 'amount': _tx_item['output'][3*i + 2].rstrip('0').rstrip('.')})
            _tx_detail_info['output_num'] += 1
            if income_address and income_address == _tx_item['output'][3*i + 1]:
                _tx_detail_info['income'] += Decimal(_tx_item['output'][3*i + 2])
        if len(_tx_detail_info['output_tx']) > show_address_num:
            _tx_detail_info['output_tx_hide'] = _tx_detail_info['output_tx'][show_address_num:]
            _tx_detail_info['output_tx_hide_num'] = len(_tx_detail_info['output_tx_hide'])
            _tx_detail_info['output_tx'] = _tx_detail_info['output_tx'][0:show_address_num]
        else:
            _tx_detail_info['output_tx_hide'] = None
        if income_address:
            _tx_detail_info['income'] = str(_tx_detail_info['income']).rstrip('0').rstrip('.')
        if _tx_detail_info['lbtc_input'] == '0':
            _tx_detail_info['fee'] = '0'
        else:
            _tx_detail_info['fee'] = _tx_detail_info['lbtc_input'] - _tx_detail_info['lbtc_output']
        if _tx_detail_info['lbtc_input'] != '0':
            _tx_detail_info['lbtc_input'] = \
                str(_tx_detail_info['lbtc_input']).rstrip('0').rstrip('.')
        _tx_detail_info['lbtc_output'] = str(_tx_detail_info['lbtc_output']).rstrip('0').rstrip('.')

        tx_info.append(_tx_detail_info)
    return tx_info


def getrawtransactionnewinfo(rpc_connection, _tx_id_list):
    _tx_list = []
    vin_tx_id = []
    tx_id_to_raw_tx_info = {}
    tx_mongos = []
    for _tx_id in _tx_id_list:
        try:
            tx_info = rpc_connection.gettransactionnew(_tx_id)
        except Exception:
            return _tx_list
        tx_mongo = {'_id': _tx_id,
                    'time': datetime.datetime.fromtimestamp(tx_info['time']),
                    'size': tx_info['vsize'],
                    'height': tx_info['height'],
                    'input': [],
                    'output': []}
        tx_id_to_raw_tx_info[_tx_id] = tx_info
        for _vin in tx_info['vin']:
            if 'coinbase' in _vin:
                pass
            else:
                vin_tx_id.append(_vin['txid'])
        vout_index = 0
        for _vout in tx_info['vout']:
            if _vout['n'] != vout_index:
                raise(ValueError('vout index error'))
            if _vout['scriptPubKey']['type'] == 'pubkeyhash' or \
               _vout['scriptPubKey']['type'] == 'scripthash':
                if len(_vout['scriptPubKey']['addresses']) != 1:
                    raise ValueError('vout multi addresses')
                tx_mongo['output'] += [_vout['n'], _vout['scriptPubKey']['addresses'][0],
                                       str(_vout['value'])]
            elif _vout['scriptPubKey']['type'] == 'nulldata':
                tx_mongo['output'] += [_vout['n'], 'nulldata', str(_vout['value'])]
            else:
                raise(ValueError('vout type unknow'))
            vout_index += 1
        _tx_list.append(tx_mongo)
        tx_mongos.append(tx_mongo)

    old_mongo_tx_info_map = {}
    if vin_tx_id:
        old_mongo_tx_info = find_many_tx(vin_tx_id)
        for item in old_mongo_tx_info:
            old_mongo_tx_info_map[item['_id']] = item
        for item in tx_mongos:
            old_mongo_tx_info_map[item['_id']] = item
    for _tx_info_mongo in tx_mongos:
        tx_info = tx_id_to_raw_tx_info[_tx_info_mongo['_id']]
        for _vin in tx_info['vin']:
            if 'coinbase' in _vin:
                _tx_info_mongo['input'] += ['coinbase', '']
            else:
                if _vin['txid'] not in old_mongo_tx_info_map:
                    tx_info_temp = rpc_connection.gettransactionnew(_vin['txid'])
                    #print('tx_info_temp', tx_info_temp['vout'])
                    #[_vout['n'], _vout['scriptPubKey']['addresses'][0], str(_vout['value'])]
                    _tx_info_mongo['input'] += \
                        [tx_info_temp['vout'][_vin['vout']]['scriptPubKey']['addresses'][0],
                         str(tx_info_temp['vout'][_vin['vout']]['value'])]
                else :
                    _tx_info_mongo['input'] += \
                        [old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 1],
                         old_mongo_tx_info_map[_vin['txid']]['output'][_vin['vout'] * 3 + 2]]
        if not _tx_info_mongo['input']:
            _tx_info_mongo['input'] = ['', '0']
    return _tx_list


@app.route('/lbtc/get_block', methods=['GET'])
def lbtc_block():
    block_hash = request.args.get('hash', None)
    height = None
    if not block_hash:
        height = int(request.args.get('height', '0').replace(',', ''))
        if not height:
            if 'language' in session and session['language'] == 'cn':
                flash(u'区块Hash或高度错误', 'error')
            else:
                flash(u'Block Hash or Height error', 'error')
            return redirect(url_for('lbtc_index'))
    rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
    try:
        if height:
            block_hash = rpc_connection.getblockhash(height)
        if not block_hash:
            if 'language' in session and session['language'] == 'cn':
                flash(u'区块Hash或高度错误', 'error')
            else:
                flash(u'Block Hash or Height error', 'error')
            return redirect(url_for('lbtc_index'))
        _info_block = rpc_connection.getblock(block_hash)
    except Exception:
        if 'language' in session and session['language'] == 'cn':
            flash(u'区块Hash或高度错误', 'error')
        else:
            flash(u'Block Hash or Height error', 'error')
        return redirect(url_for('lbtc_index'))
    if not _info_block:
        if 'language' in session and session['language'] == 'cn':
            flash(u'区块Hash或高度错误', 'error')
        else:
            flash(u'Block Hash or Height error', 'error')
        return redirect(url_for('lbtc_index'))

    _tx_id_list = []
    for _tx_id in _info_block['tx']:
        _tx_id_list.append(_tx_id)
    _tx_list = find_many_tx(_tx_id_list)
    if not _tx_list:
        _tx_list = getrawtransactionnewinfo(rpc_connection, _tx_id_list)
        if not _tx_list:
            if 'language' in session and session['language'] == 'cn':
                flash(u'区块Hash或高度错误', 'error')
            else:
                flash(u'Block Hash or Height error', 'error')
            return redirect(url_for('lbtc_index'))

    tx_info = []
    key_list = [PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT,
                REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME]
    block_status_multi_key_value = get_block_status_multi_key(key_list)
    current_height = \
        block_status_multi_key_value[PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT]['height']
    tx_info = get_tx_detail_info(_tx_list, current_height=current_height,
                                 confirmations=_info_block['confirmations'])
    block_info = {'tx_info': tx_info}
    for key in ['merkleroot', 'nonce', 'previousblockhash', 'hash', 'height', 'confirmations',
                'time', 'versionHex', 'strippedsize', 'tx']:
        block_info[key] = _info_block[key]
    block_info['time'] = \
        datetime.datetime.fromtimestamp(block_info['time']).strftime('%Y-%m-%d %H:%M:%S')
    block_info['transaction_num'] = len(_info_block['tx'])

    coinbase_tx = query_coinbase_tx(_info_block['tx'])
    if not coinbase_tx:
        coinbase_tx = _tx_list[0:1]
    if len(coinbase_tx) != 1:
        if 'language' in session and session['language'] == 'cn':
            flash(u'区块数据未同步', 'error')
        else:
            flash(u'Block Hash or Height error', 'error')
        return redirect(url_for('lbtc_index'))
    block_info['delegate_address'] = coinbase_tx[0]['output'][1]
    delegate_address_to_name = \
        block_status_multi_key_value[REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME]
    block_info['miner_name'] = delegate_address_to_name[block_info['delegate_address']]

    try:
        block_info['next_hash'] = rpc_connection.getblockhash(_info_block['height'] + 1)
    except Exception:
        #traceback.print_exc()
        block_info['next_hash'] = ''
    block_info['height'] = '{:,}'.format(block_info['height'])
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/block.html'
    else:
        template_name = 'en/block.html'
    return render_template(template_name, block_info=block_info, show_tx_hash=True, float=float)


@app.route('/lbtc/search', methods=['GET'])
def lbtc_search():
    param = request.args.get('param', '')
    param = param.strip(' ')
    if not param:
        if 'language' in session and session['language'] == 'cn':
            flash(u'没有搜索到您查找的结果,请检查输入是否正确', 'error')
        else:
            flash(u'Sorry: Not Found', 'error')
        return redirect(url_for('lbtc_index'))
    height = None
    try:
        height = int(param)
    except ValueError:
        pass
    if height:
        return redirect(url_for('lbtc_block', height=height))
    try:
        rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
        _info_block = rpc_connection.getblock(param)
        return redirect(url_for('lbtc_block', hash=param))
    except JSONRPCException:
        pass
    _address_info = query_address_info(param)
    if _address_info or param in address_to_no_mongo_tx:
        return redirect(url_for('lbtc_address', address=param))
    _tx_info = find_one_tx(param)
    if _tx_info:
        return redirect(url_for('lbtc_tx', hash=param))
    _tx_info = getrawtransactionnewinfo(rpc_connection, [param])
    if _tx_info:
        return redirect(url_for('lbtc_tx', hash=param))
    key_list = [REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS,
                REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS]
    block_status_multi_key_value = get_block_status_multi_key(key_list)
    if param in block_status_multi_key_value[REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS]:
        delegate_address = \
            block_status_multi_key_value[REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS][param]
        return redirect(url_for('lbtc_address', address=delegate_address))
    if param in block_status_multi_key_value[REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS]:
        committee_address = \
            block_status_multi_key_value[REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS][param]
        return redirect(url_for('lbtc_address', address=committee_address))

    return redirect(url_for('lbtc_bill', id=param))


@app.route('/lbtc/balance', methods=['GET'])
def lbtc_balance():
    address_distribution = [[0, 0.001], [0.001, 0.01], [0.01, 0.1], [0.1, 1], [1, 10],
                            [10, 1000], [1000, 10000], [10000, 99999999]]
    balance_distribution = get_balance_distribution(address_distribution)
    address_count = 0
    balance_total = 0
    address_stats = {'count': [], 'percent': []}
    balance_stats = {'count': [], 'percent': []}
    address_distribution_label = []
    for i in range(0, len(address_distribution)):
        if i == len(address_distribution) - 1:
            address_distribution_label.append(str(address_distribution[i][0]) + '-1000000')
        else:
            address_distribution_label.append(str(address_distribution[i][0]) + '-' + str(address_distribution[i][1]))
        address_count += balance_distribution[2*i]
        address_stats['count'].append(balance_distribution[2*i])
        balance_total += balance_distribution[2*i + 1]
        balance_stats['count'].append(balance_distribution[2*i + 1])
    for i in range(0, len(address_distribution)):
        address_stats['percent'].append('{0:.2f}%'.format(100 * balance_distribution[2*i] / address_count))
        balance_stats['percent'].append('{0:.2f}%'.format(100 * balance_distribution[2*i + 1] / balance_total))

    balance_info = query_most_rich_address(REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST,
                                           REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO)
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/balance.html'
    else:
        template_name = 'en/balance.html'
    return render_template(template_name, balance_info=balance_info, address_distribution=address_distribution,
                           address_count=address_count, address_stats=address_stats,
                           balance_total=balance_total, balance_stats=balance_stats,
                           address_distribution_label = address_distribution_label)


@app.route('/lbtc/committee', methods=['GET'])
def lbtc_committee():
    committee_info = query_all_committee()
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/committee.html'
    else:
        template_name = 'en/committee.html'
    return render_template(template_name, committee_info=committee_info)


@app.route('/lbtc/proposal', methods=['GET'])
def lbtc_proposal():
    proposal_info = query_all_proposal()
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/proposal.html'
    else:
        template_name = 'en/proposal.html'
    return render_template(template_name, proposal_info=proposal_info)


@app.route('/lbtc/bill', methods=['GET'])
def lbtc_bill():
    bill_id = request.args.get('id', '')
    bill_id = bill_id.strip(' ')
    if not bill_id:
        if 'language' in session and session['language'] == 'cn':
            flash(u'提案ID错误', 'error')
        else:
            flash(u'Proposal ID error', 'error')
        return redirect(url_for('lbtc_index'))
    proposal_info = query_all_proposal(bill_id=bill_id)
    if not proposal_info:
        if 'language' in session and session['language'] == 'cn':
            flash(u'没有搜索到您查找的结果,请检查输入是否正确', 'error')
        else:
            flash(u'Sorry: Not Found', 'error')
        return redirect(url_for('lbtc_index'))
    show_address_num = 5
    option_index = 1
    for _option in proposal_info["options"]:
        if len(_option['vote_address']) > show_address_num:
            _option['vote_address_hide'] = _option['vote_address'][show_address_num:]
            _option['vote_address_hide_num'] = len(_option['vote_address_hide'])
            _option['vote_address'] = _option['vote_address'][0:show_address_num]
            _option['vote_collapse_href'] = '#collapseVote' + str(option_index)
            _option['vote_collapse_id'] = 'collapseVote' + str(option_index)
        else:
            _option['vote_address_hide'] = None
        option_index += 1

    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/proposal_detail.html'
    else:
        template_name = 'en/proposal_detail.html'
    return render_template(template_name, proposal_info=proposal_info)


@app.route('/lbtc/delegate_api', methods=['GET'])
@limiter.limit("40/minute")
def lbtc_delegate_api():
    delegate_type = request.args.get('type', '')
    global delegate_count_global
    global normal_count_global
    global stop_count_global
    global delegate_info_global
    global delegate_info_global_update_time
    time_now = datetime.datetime.now()
    if delegate_info_global_update_time is None or \
       (time_now - delegate_info_global_update_time).total_seconds() > 0.2:
        delegate_info_global_update_time = time_now
        delegate_count_global = 0
        normal_count_global = 0
        stop_count_global = 0
        delegate_info_global = query_all_delegate()
        current_delegate = get_block_status(REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE)['current_delegate']
    
        current_delegate_dict = {}
        for _delegate in current_delegate:
            current_delegate_dict[_delegate] = 1
        
        delegate_info_filter = []
        index = 1
        for _delegate in delegate_info_global:
            _delegate['ratio'] = '{0:.2f}%'.format(_delegate.get('ratio', 0) * 100)
            delegate_count_global += 1
            if _delegate['_id'] in current_delegate_dict:
                if _delegate['status'] == 1:
                    normal_count_global += 1
                else:
                    stop_count_global += 1
            if delegate_type == 'active':
                if _delegate['_id'] in current_delegate_dict:
                    delegate_info_filter.append(_delegate)
            elif delegate_type == 'normal':
                if _delegate['_id'] in current_delegate_dict and _delegate['status'] == 1:
                    _delegate['index'] = index
                    delegate_info_filter.append(_delegate)
            elif delegate_type == 'stop':
                if _delegate['_id'] in current_delegate_dict and _delegate['status'] == 0:
                    _delegate['index'] = index
                    index += 1
                    delegate_info_filter.append(_delegate)
        if delegate_info_filter:
            delegate_info_global = delegate_info_filter
        address_to_delegate = {}
        if delegate_type == 'active' or delegate_type == 'normal':
            for _delegate in delegate_info_global:
                address_to_delegate[_delegate['_id']] = _delegate
            delegate_info_global = []
            for _delegate in current_delegate:
                if _delegate in address_to_delegate:
                    address_to_delegate[_delegate]['index'] = index
                    if 'block_product' in address_to_delegate[_delegate]:
                        address_to_delegate[_delegate].pop('block_product')
                    if 'block_vote' in address_to_delegate[_delegate]:
                        address_to_delegate[_delegate].pop('block_vote')
                    delegate_info_global.append(address_to_delegate[_delegate])
                    index += 1
    ret = {'delegate_info': delegate_info_global, 'type': delegate_type,
           'delegate_count': delegate_count_global, 'normal_count': normal_count_global,
           'stop_count': stop_count_global}
    return jsonify(ret)


@app.route('/lbtc/delegate', methods=['GET'])
def lbtc_delegate():
    delegate_type = request.args.get('type', '')
    delegate_info = query_all_delegate()
    current_delegate = get_block_status(REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE)['current_delegate']

    current_delegate_dict = {}
    for _delegate in current_delegate:
        current_delegate_dict[_delegate] = 1
    
    delegate_count = 0
    normal_count = 0
    stop_count = 0
    delegate_info_filter = []
    index = 1
    for _delegate in delegate_info:
        _delegate['ratio'] = '{0:.2f}%'.format(_delegate.get('ratio', 0) * 100)
        delegate_count += 1
        if _delegate['_id'] in current_delegate_dict:
            if _delegate['status'] == 1:
                normal_count += 1
            else:
                stop_count += 1
        if delegate_type == 'active':
            if _delegate['_id'] in current_delegate_dict:
                delegate_info_filter.append(_delegate)
        elif delegate_type == 'normal':
            if _delegate['_id'] in current_delegate_dict and _delegate['status'] == 1:
                _delegate['index'] = index
                delegate_info_filter.append(_delegate)
        elif delegate_type == 'stop':
            if _delegate['_id'] in current_delegate_dict and _delegate['status'] == 0:
                _delegate['index'] = index
                index += 1
                delegate_info_filter.append(_delegate)
    if delegate_info_filter:
        delegate_info = delegate_info_filter
    address_to_delegate = {}
    if delegate_type == 'active' or delegate_type == 'normal':
        for _delegate in delegate_info:
            address_to_delegate[_delegate['_id']] = _delegate
        delegate_info = []
        for _delegate in current_delegate:
            if _delegate in address_to_delegate:
                address_to_delegate[_delegate]['index'] = index
                delegate_info.append(address_to_delegate[_delegate])
                index += 1
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/delegate.html'
    else:
        template_name = 'en/delegate.html'
    return render_template(template_name, delegate_info=delegate_info, type=delegate_type,
                           delegate_count=delegate_count, normal_count=normal_count,
                           stop_count=stop_count)


def get_address_extra_tx(rpc_connection, address, address_tx_height, current_height, best_height):
    global address_to_no_mongo_tx
    global memcache_block_height
    global memcache_reset_time
    time_now = datetime.datetime.now()
    if memcache_block_height == 0:
        memcache_reset_time = time_now
    else:
        if (time_now - memcache_reset_time).total_seconds() > 30:
            memcache_reset_time = time_now
            memcache_block_height = 0
            address_to_no_mongo_tx = {}

    extra_tx = []
    start_height = 0
    if memcache_block_height > current_height:
        start_height = memcache_block_height
    else:
        start_height = current_height
    next_block_hash = ''
    _tx_id_list = []
    try:
        while start_height <= best_height:
            if not next_block_hash:
                next_block_hash = rpc_connection.getblockhash(start_height)
            block = rpc_connection.getblock(next_block_hash)
            if not block:
                return extra_tx
            next_block_hash = block.get('nextblockhash', '')
            _tx_id_list += block['tx']
            start_height += 1
    except Exception:
        return extra_tx
    if _tx_id_list:
        extra_tx = getrawtransactionnewinfo(rpc_connection, _tx_id_list)
    address_to_no_mongo_tx_local = {}
    for _address in address_to_no_mongo_tx:
        no_mongo_tx = []
        for _tx in address_to_no_mongo_tx[_address]:
            if _tx['height'] >= current_height:
                no_mongo_tx.append(_tx)
        address_to_no_mongo_tx_local[_address] = no_mongo_tx
    address_to_no_mongo_tx = address_to_no_mongo_tx_local

    for _tx in extra_tx:
        contain_address = set()
        for i in range(0, len(_tx['input']) // 2):
            if _tx['input'][2*i] != 'coinbase':
                contain_address.add(_tx['input'][2*i])
        for i in range(0, len(_tx['output']) // 3):
            if _tx['output'][3*i + 1] != 'nulldata':
                contain_address.add(_tx['output'][3*i + 1])
        for _address in contain_address:
            if _address not in address_to_no_mongo_tx:
                address_to_no_mongo_tx[_address] = []
            address_to_no_mongo_tx[_address].append(_tx)
    memcache_block_height = best_height + 1
    extra_tx = []
    for _tx in address_to_no_mongo_tx.get(address, []):
        if _tx['height'] > address_tx_height:
            extra_tx.insert(0, _tx)
    return extra_tx


@app.route('/lbtc/daily_tx', methods=['GET'])
def lbtc_daily_tx():
    start_time = request.args.get('start_time', '')
    end_time = request.args.get('end_time', '')
    if not start_time or not end_time:
        return 'wrong time'
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
    end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
    #print(start_time, end_time)
    ret = get_block_during(start_time, end_time)
    start_height = ret[0]
    end_height = ret[1]
    #print(start_height, end_height)

    next_block_hash = ''
    current_height = start_height
    _tx_id_list = []
    rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
    for i in range(start_height, end_height+1):
        block_info = {}
        if not next_block_hash:
            next_block_hash = rpc_connection.getblockhash(current_height)
        block = rpc_connection.getblock(next_block_hash)
        if not block:
            flash(u'区块高度错误', 'error')
            return u'区块高度错误'
        next_block_hash = block['nextblockhash']
        for _tx_id in block['tx']:
            _tx_id_list.append(_tx_id)
    _tx_list = find_many_tx(_tx_id_list)
    show_txs = []
    for _tx in _tx_list:
        amount = 0
        for i in range(0, len(_tx['output']) // 3):
            if _tx['output'][3*i + 1] == 'nulldata':
                continue
            amount += float(_tx['output'][3*i + 2])
        if amount > 50:
            show_txs.append(_tx)
    #print(_tx_list[0])
    #print('len(show_txs)', len(show_txs))
    show_txs.sort(key=lambda x: x['height'], reverse=False)
    block_info = {'previousblockhash': '', 'miner_name': '', 'delegate_address': '',
                  'versionHex': '', 'height': '0', 'strippedsize': 0, 'tx': [''],
                  'confirmations': 0, 'next_hash': '', 'transaction_num': len(show_txs), 'merkleroot': '', 'hash': '',
                  'time': '', 'nonce': 0}
    block_info['tx_info'] = get_tx_detail_info(show_txs, current_height=end_height+2)
    global address_to_remark
    for _tx in block_info['tx_info']:
        for _output in _tx['output_tx']:
            if address_to_remark.get(_output['address'], ''):
                _output['address'] += '(' + address_to_remark.get(_output['address'], '') + ')'
        for _input in _tx['input_tx']:
            if address_to_remark.get(_input['address'], ''):
                _input['address'] += '(' + address_to_remark.get(_input['address'], '') + ')'
    #print(block_info['tx_info'][0])
    return render_template('en/block.html', block_info=block_info, show_tx_hash=True, float=float)


@app.route('/lbtc/address', methods=['GET'])
def lbtc_address():
    address = request.args.get('address', '')
    address = address.strip(' ')
    tx_per_page = 10
    current_page = int(request.args.get('page', 1))
    if not address or current_page < 1:
        if 'language' in session and session['language'] == 'cn':
            flash(u'钱包地址或页码错误', 'error')
        else:
            flash(u'Address Or Page error', 'error')
        return redirect(url_for('lbtc_index'))
    _address_info = get_address_info(address, page=current_page, size=tx_per_page)
    if not _address_info:
        if address in address_to_no_mongo_tx:
            _address_info = {'address': address,
                             'tx': [],
                             'send': '0',
                             'receive': '0',
                             'update_time': '',
                             'create_time': '',
                             'tx_num': 0}
    if not _address_info:
        if 'language' in session and session['language'] == 'cn':
            flash(u'钱包地址错误', 'error')
        else:
            flash(u'Address error', 'error')
        return redirect(url_for('lbtc_index'))
    address_tx_hash = []
    for _tx_item in _address_info['tx']:
        address_tx_hash.append(_tx_item['hash'])
    address_tx_info = find_many_tx(address_tx_hash, sort=True)

    key_list = [PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT,
                REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME,
                REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME]
    block_status_multi_key_value = get_block_status_multi_key(key_list)
    best_height = \
        block_status_multi_key_value[PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT]['best_height']
    rpc_connection = None
    update_time = None
    extra_tx = []
    if current_page == 1:
        rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
        address_balance = float(rpc_connection.getaddressbalance(address)) / 100000000
        current_height = \
            block_status_multi_key_value[PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT]['height']
        if address_tx_info:
            extra_tx = get_address_extra_tx(rpc_connection, address, address_tx_info[0]['height'], current_height, best_height - 3)
        else:
            extra_tx = get_address_extra_tx(rpc_connection, address, 0, current_height, best_height - 3)
        if extra_tx:
            update_time = extra_tx[0]['time'].isoformat().replace('T', ' ')
        else:
            update_time = _address_info['update_time'].replace('T', ' ')
    else:
        address_balance = "{:.8f}".format(Decimal(_address_info['balance'])).rstrip('0').rstrip('.')
        update_time = _address_info['update_time'].replace('T', ' ')

    tx_info = get_tx_detail_info(extra_tx + address_tx_info, current_height=best_height, income_address=address)
    address_info = {'address': address,
                    'balance': address_balance,
                    'transaction_num': _address_info['tx_num'] + len(extra_tx),
                    'create_time': _address_info['create_time'].replace('T', ' '),
                    'update_time': update_time,
                    'receive': _address_info['receive'].rstrip('0').rstrip('.'),
                    'send': "{:.8f}".format(float(_address_info['send'])).rstrip('0').rstrip('.'),
                    'tx_info': tx_info}
    tx_count = _address_info['tx_num']
    total_page = (tx_count + (tx_per_page - 1)) // tx_per_page
    min_page = max(1, current_page - 2)
    max_page = min(total_page, current_page + 2)
    if current_page == 1:
        current_page_up = 0
    else:
        current_page_up = current_page - 1
    if current_page == total_page:
        current_page_next = 0
    else:
        current_page_next = current_page + 1
    if current_page == 1:
        try:
            voted_delegates = rpc_connection.listvoteddelegates(address)
            delegate_address_to_name = \
                block_status_multi_key_value[REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME]
            if address in delegate_address_to_name:
                delegate_name = delegate_address_to_name[address]
                if delegate_name == 'LBTCSuperNode':
                    delegate_received_voter = []
                else:
                    delegate_received_voter = rpc_connection.listreceivedvotes(delegate_name)
            else:
                delegate_received_voter = []
                delegate_name = None

            voted_committees = rpc_connection.listvotercommittees(address)
            committee_address_to_name = \
                block_status_multi_key_value[REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME]
            if address in committee_address_to_name:
                committee_name = committee_address_to_name[address]
                committee_received_voter_list = rpc_connection.listcommitteevoters(committee_name)
                committee_received_voter = []
                for item in committee_received_voter_list:
                    committee_received_voter.append(item['address'])
                submit_bills = rpc_connection.listcommitteebills(committee_name)
            else:
                committee_received_voter = []
                committee_name = None
                submit_bills = []
            voted_bills = rpc_connection.listvoterbills(address)

            voted_delegates_num = len(voted_delegates)
            delegate_received_voter_num = len(delegate_received_voter)
            voted_committees_num = len(voted_committees)
            committee_received_voter_num = len(committee_received_voter)
            voted_bills_num = len(voted_bills)
            submit_bills_num = len(submit_bills)
        except Exception as e:
            print(e)
            if 'language' in session and session['language'] == 'cn':
                flash(u'钱包地址错误', 'error')
            else:
                flash(u'Address error', 'error')
            return redirect(url_for('lbtc_index'))
    else:
        voted_delegates = None
        delegate_received_voter = None
        delegate_address_to_name = None
        delegate_name = None

        voted_committees = None
        committee_received_voter = None
        committee_address_to_name = None
        committee_name = None

        submit_bills = None
        voted_bills = None

        voted_delegates_num = 0
        delegate_received_voter_num = 0
        voted_committees_num = 0
        committee_received_voter_num = 0
        voted_bills_num = 0
        submit_bills_num = 0
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/address.html'
    else:
        template_name = 'en/address.html'
    if request.args.get('remark', '') == 'remark':
        global address_to_remark
        for _tx in address_info['tx_info']:
            for _output in _tx['output_tx']:
                if address_to_remark.get(_output['address'], ''):
                    _output['address'] += '(' + address_to_remark.get(_output['address'], '') + ')'
            for _input in _tx['input_tx']:
                if address_to_remark.get(_input['address'], ''):
                    _input['address'] += '(' + address_to_remark.get(_input['address'], '') + ')'
    return render_template(template_name, address_info=address_info, not_href_address=address,
                           show_income=True, show_tx_hash=True, show_tx_height=True,
                           show_tx_time=True, float=float,
                           address=address,
                           current_page=current_page,
                           current_page_up=current_page_up,
                           current_page_next=current_page_next,
                           total_page=total_page,
                           min_page=min_page,
                           max_page=max_page,
                           voted_delegates=voted_delegates,
                           delegate_received_voter=delegate_received_voter,
                           delegate_address_to_name=delegate_address_to_name,
                           delegate_name=delegate_name,
                           voted_committees=voted_committees,
                           committee_received_voter=committee_received_voter,
                           committee_address_to_name=committee_address_to_name,
                           committee_name=committee_name,
                           submit_bills=submit_bills,
                           voted_bills=voted_bills,
                           voted_delegates_num=voted_delegates_num,
                           delegate_received_voter_num=delegate_received_voter_num,
                           voted_committees_num=voted_committees_num,
                           committee_received_voter_num=committee_received_voter_num,
                           voted_bills_num=voted_bills_num,
                           submit_bills_num=submit_bills_num,)


@app.route('/lbtc/tx', methods=['GET'])
def lbtc_tx():
    tx_hash = request.args.get('hash', '')
    if not tx_hash:
        if 'language' in session and session['language'] == 'cn':
            flash(u'交易hash错误', 'error')
        else:
            flash(u'Tx Hash error', 'error')
        return redirect(url_for('lbtc_index'))
    current_height = get_block_status(PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT)['best_height']
    _tx_list = find_one_tx(tx_hash)
    if not _tx_list:
        rpc_connection = AuthServiceProxy('http://%s:%s@127.0.0.1:9332' % ('luyao', 'DONNNN'))
        _tx_list = getrawtransactionnewinfo(rpc_connection, [tx_hash])
        if not _tx_list:
            if 'language' in session and session['language'] == 'cn':
                flash(u'交易hash错误', 'error')
            else:
                flash(u'Tx Hash error', 'error')
            return redirect(url_for('lbtc_index'))
    else:
        _tx_list = [_tx_list]
    tx_info = get_tx_detail_info(_tx_list, current_height=current_height)
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/tx.html'
    else:
        template_name = 'en/tx.html'
    return render_template(template_name, tx_info=tx_info[0],
                           show_income=False, show_tx_height=True)


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
    node_type = int(request.args.get('type', '0'))
    all_node = get_all_node(2, country=country)

    if 'language' in session and session['language'] == 'cn':
        if not country:
            if node_type == 1:
                country = u'所有地区可连接节点列表'
            elif node_type == 2:
                country = u'所有地区不可连接节点列表'
            elif node_type == 4:
                country = u'所有地区IPv4节点列表'
            elif node_type == 6:
                country = u'所有地区IPv6节点列表'
            elif node_type == 5:
                country = u'所有地区onion节点列表'
            else:
                country = u'所有地区节点列表'
        else:
            if node_type == 1:
                country += u' 可连接节点列表'
            elif node_type == 2:
                country += u' 不可连接节点列表'
            elif node_type == 4:
                country += u' IPv4节点列表'
            elif node_type == 6:
                country += u' IPv6节点列表'
            elif node_type == 5:
                country += u' onion节点列表'
            else:
                country += u' 节点列表'
    else:
        if not country:
            if node_type == 1:
                country = u'All Connected Nodes'
            elif node_type == 2:
                country = u'All Not Connected Nodes'
            elif node_type == 4:
                country = u'All IPv4 Nodes'
            elif node_type == 6:
                country = u'All IPv6 Nodes'
            elif node_type == 5:
                country = u'All onion Nodes'
            else:
                country = u'All Nodes'
        else:
            if node_type == 1:
                country += u' Connected Nodes'
            elif node_type == 2:
                country += u' Not Connected Nodes'
            elif node_type == 4:
                country += u' IPv4 Nodes'
            elif node_type == 6:
                country += u' IPv6 Nodes'
            elif node_type == 5:
                country += u' onion Nodes'
            else:
                country += u' All Nodes'
    valid_node = []
    if node_type == 4:
        for _node in all_node:
            if not _node['ip'].endswith(".onion") and len(_node['ip'].split(':')) == 2:
                valid_node.append(_node)
    elif node_type == 6:
        for _node in all_node:
            if not _node['ip'].endswith(".onion") and len(_node['ip'].split(':')) > 2:
                valid_node.append(_node)
    elif node_type == 5:
        for _node in all_node:
            if _node['ip'].endswith(".onion"):
                valid_node.append(_node)
    elif node_type == 1:
        for _node in all_node:
            if '(not connected' not in _node['user_agent']:
                valid_node.append(_node)
    elif node_type == 2:
        for _node in all_node:
            if '(not connected' in _node['user_agent']:
                valid_node.append(_node)
    else:
        valid_node = all_node
    # valid_node = sorted(all_node, cmp=node_cmp)
    count = 1
    for _node in valid_node:
        _node['id'] = count
        count += 1
    if 'language' in session and session['language'] == 'cn':
        template_name = 'cn/node.html'
    else:
        template_name = 'en/node.html'
    return render_template(template_name, all_node=valid_node, country=country,
                           node_distribution=node_distribution, node_status=node_status)


@app.route('/lbtc/change_language')
def lbtc_change_language():
    if request.args.get('language', '') in ['cn', 'en']:
        session["language"] = request.args['language']
        return redirect(url_for('lbtc_index'))
    else:
        if 'language' in session and session['language'] == 'cn':
            flash(u"参数错误", 'error')
        else:
            flash(u'parameter error', 'error')
        return redirect(url_for('lbtc_index'))


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
    if not getattr(g, 'log_info', None):
        response.headers['Date'] = \
            datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        return response
    g.log_info['end_time'] = time.time()
    g.log_info['process_time'] = \
        g.log_info['end_time'] - g.log_info['start_time']

    g.log_info['status_code'] = response.status_code
    g.log_info['ret_headers'] = dict(response.headers)

    if 400 <= response.status_code < 500:
        rest_log.logger.warning(g.log_info)
    else:
        if '/static' not in request.url:
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
    app.config['DEBUG'] = False
    app.run(host='0.0.0.0', port=5025)
