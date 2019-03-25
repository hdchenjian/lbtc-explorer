#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from v8.config import config_online


V8_CONFIG = config_online

# martin REST fluentd logger
REST_TD_HOST = 'localhost'
REST_TD_PORT = 24224
REST_TD_LOG = 'martin_rest'
REST_LOG_FILE_LEVEL = logging.DEBUG
