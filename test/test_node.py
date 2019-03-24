#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests

host = 'http://localhost:5024'
# host = 'http://104.224.136.93:5000'
# host = 'https://www.green-reading.com/api/firm'


def test_get_update_info():
    ret = requests.get(
        host+'/update_info',
        params={'device_id': 'test11',
                'current_alg_version': '1000',
                'appname': 'danki_v4',
                'fpga_version': '1.1',
                'current_firm_version': 'CG_V100R001B001SP07'})
    print(ret.content)


def test_upload_device_info():
    data = {
        'device_id': 'test11',
        'current_p2p': 1,
        'current_alg_version': '1000',
        'current_firm_version': 'CG_V100R001B001SP07',
        'appid': '1',
        'appname': 'danki_v4',
        'fpga_version': '1.1'
    }
    ret = requests.post(
        host+'/upload_device_info',
        data=data)
    print(ret.content)


if __name__ == '__main__':
    test_get_update_info()
    # test_upload_device_info()
