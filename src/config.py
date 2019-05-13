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
REST_BLOCK_STATUS_KYE_COMMITTEE_ADDRESS_TO_NAME = 'rest_block_status:key_committee_address_to_name'
REST_BLOCK_STATUS_KYE_DELEGATE_NAME_TO_ADDRESS = 'rest_block_status:key_delegate_name_to_address'
REST_BLOCK_STATUS_KYE_COMMITTEE_NAME_TO_ADDRESS = 'rest_block_status:key_committee_name_to_address'
REST_BLOCK_STATUS_KYE_TX_OUT_SET_INFO = 'rest_block_status:key_tx_out_set_info'
REST_BLOCK_STATUS_KYE_RICHEST_ADDRESS_LIST = 'rest_block_status:key_richest_address_list'
REST_BLOCK_STATUS_KYE_NETWORK_TX_STATISTICS = 'rest_block_status:key_network_tx_statistics'
REST_BLOCK_STATUS_KYE_CURRENT_DELEGATE = 'rest_block_status:key_current_delegate'

PARSE_BLOCK_STATUS_KYE_MYSQL_CURRENT_HEIGHT = 'parse_block_status:kye_mysql_current_height'
PARSE_BLOCK_STATUS_KYE_MYSQL_VALID_TX_HEIGHT = 'parse_block_status:kye_mysql_valid_tx_height'
