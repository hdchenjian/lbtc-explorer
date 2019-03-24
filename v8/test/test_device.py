#!/usr/bin/python
# -*- coding: utf-8 -*-

from v8.config import config, config_test, config_online
from v8.engine.handlers.update_device import \
    save_device_info, get_device_info, get_max_id_with_page, \
    get_active_device_stat, update_active_devices

test = False
if test:
    config.from_object(config_test)
    print("test environment")
else:
    config.from_object(config_online)
    print("online environment")


def test_save_device_info():
    save_device_info(11, '1.1', '1.0', 1)


def test_get_device_info():
    since_id = 0
    page_num = 10
    ret = get_device_info(since_id, page_num)
    for device in ret:
        print(device['id'])


def test_get_max_id_with_page():
    current_page = 4
    device_per_page = 4
    print(get_max_id_with_page(current_page, device_per_page)['device_id'])


def test_get_active_device_stat():
    get_active_device_stat()


def test_update_active_devices():
    active_minute = 49
    firm_version = '1'
    print(update_active_devices(active_minute, firm_version))


if __name__ == '__main__':
    # test_save_device_info()
    # test_get_device_info()
    # test_get_max_id_with_page()
    # test_get_active_device_stat()
    test_update_active_devices()
