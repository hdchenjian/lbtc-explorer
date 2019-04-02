#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging

# REST fluentd logger
REST_TD_HOST = 'localhost'
REST_TD_PORT = 24224
REST_TD_LOG = 'lbtc_rest'
REST_LOG_FILE_LEVEL = logging.DEBUG

REST_BLOCK_STATUS_KYE_NODE_IP_TYPE = 'rest_block_status:key_node_ip_type'
REST_BLOCK_STATUS_KYE_DELEGATE_ADDRESS_TO_NAME = 'rest_block_status:key_delegate_address_to_name'
REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO = 'rest_block_status:key_tx_out_set_info'
REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST = 'rest_block_status:key_richest_address_list'

PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT = 'parse_block_status:kye_mysql_current_height'
