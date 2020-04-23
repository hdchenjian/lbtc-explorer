#!/usr/bin/python3
# -*- coding: utf-8 -*-

import datetime
import calendar
import time
import traceback

from flask import Flask, g, request, jsonify, render_template, \
    flash, redirect, url_for, session
import sqlite3

import rest_log

app = Flask(__name__)
app.secret_key = 'green rseading key'
app.config['SESSION_TYPE'] = 'filesystem'

def create_table():
    conn = sqlite3.connect('note.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE if not exists `day` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    `date` TEXT NOT NULL DEFAULT CURRENT_DATE,
    `event` TEXT NOT NULL DEFAULT '',
    `hours` REAL NOT NULL DEFAULT '',
    `create_time` TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()


def get_event_recent(c, start_time, end_time):
    sql = "SELECT * FROM day where date >= '%s' and date <= '%s' order by date desc" % (
        start_time.strftime("%Y-%m-%d"), end_time.strftime("%Y-%m-%d"))
    events = c.execute(sql)
    event_recent_dict = {}
    for e in events:
        if e[1] not in event_recent_dict:
            event_recent_dict[e[1]] = [0]
        event_recent_dict[e[1]].append([e[2], e[3]])
        event_recent_dict[e[1]][0] += float(e[3])
    event_recent = []
    for e in sorted(event_recent_dict.keys(), reverse=True):
        if e in event_recent_dict:
            day_event = [e, event_recent_dict[e][0], []]
            for ee in event_recent_dict[e][1:]:
                day_event[2].append(ee)
            event_recent.append(day_event)
    return event_recent


@app.route('/lbtc1/lbtc4c9508752f3c3da92432d9bd7fb0ae45ctbl', methods=['GET', 'POST'])
def lbtc_note():
    create_table()
    conn = sqlite3.connect('note.db')
    c = conn.cursor()

    try:
        now = datetime.datetime.now()
        end_time = now.date()
        start_time = end_time - datetime.timedelta(days=10)

        if request.method == 'GET':
            event_recent = get_event_recent(c, start_time, end_time)
            conn.close()
            total_hours = 0
            for e in event_recent:
                total_hours += e[1]
            return render_template('note/index.html', event_recent=event_recent, this_month=now.strftime("%Y-%m-%d"),
                                   avg_hours = total_hours / len(event_recent))
        else:
            date = request.form.get('date', '')
            event = request.form.get('event', '')
            hour = float(request.form.get('hour', 0))
            if not date or not event or hour < 0:
                conn.close()
                return u'参数不能为空'
            date = datetime.datetime.strptime(date, '%Y-%m-%d')
            latest_event = c.execute('SELECT * FROM day order by id desc limit 1').fetchone()
            if not latest_event:
                event_id = 1
            else:
                event_id = latest_event[0] + 1
            sql = "INSERT INTO day VALUES (%d, '%s', '%s', '%s', '%s')" % (
                event_id, date.strftime('%Y-%m-%d'), event, hour, now.strftime("%Y-%m-%d %H:%M:%S"))
            c.execute(sql)
            conn.commit()
            event_recent = get_event_recent(c, start_time, end_time)
            conn.close()
            total_hours = 0
            for e in event_recent:
                total_hours += e[1]
            return render_template('note/index.html', event_recent=event_recent, this_month=now.strftime("%Y-%m-%d"),
                                   avg_hours = total_hours / len(event_recent))
    except Exception as e:
        raise
        traceback.format_exc()
        print(e)
        conn.close()
        return render_template('note/index.html', event_recent=[], this_month=now.strftime("%Y-%m-%d"))


@app.route('/lbtc1/lbtc4c9508752f3c3da92432d9bd7fb0ae45ctblmonth', methods=['GET', 'POST'])
def lbtc_month():
    create_table()
    conn = sqlite3.connect('note.db')
    c = conn.cursor()
    try:
        now = datetime.datetime.now()
        month = request.args.get('month', '')
        start_time = datetime.datetime.strptime(month, '%Y-%m-%d').date().replace(day=1)
        end_time = start_time.replace(day=calendar.monthrange(start_time.year, start_time.month)[1])
        event_recent = get_event_recent(c, start_time, end_time)
        total_hours = 0
        for e in event_recent:
            total_hours += e[1]
        conn.close()
        return render_template('note/index.html', event_recent=event_recent, this_month=now.strftime("%Y-%m-%d"),
                               avg_hours = total_hours / len(event_recent))
    except Exception as e:
        raise
        traceback.format_exc()
        print(e)
        conn.close()
        return render_template('note/index.html', event_recent=[])


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
    app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5026)
