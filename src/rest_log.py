#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import sys

from fluent.handler import FluentHandler, FluentRecordFormatter

from config import REST_LOG_FILE_LEVEL, REST_TD_HOST, REST_TD_PORT, REST_TD_LOG


class RESTRecordFormatter(FluentRecordFormatter):

    def format(self, record):
        data = {'sys_host': self.hostname,
                'sys_name': record.name,
                'sys_module': record.module,
                'sys_levelname': record.levelname,
                }
        self._structuring(data, record.msg)
        return data


logger = logging.getLogger('lbtc_REST')
logger.setLevel(REST_LOG_FILE_LEVEL)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s -%(funcName)s '
    '- %(lineno)d - %(message)s')

# stream logging
sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
logger.addHandler(sh)

# fluentd handler
td_handler = FluentHandler(REST_TD_LOG, host=REST_TD_HOST, port=REST_TD_PORT)
td_handler.fmt = RESTRecordFormatter()
logger.addHandler(td_handler)
