#!/usr/bin/python
# -*- coding: utf-8 -*-

from v8.config import config, config_test, config_online
from v8.engine.handlers.user import get_user_info

test = True
if test:
    config.from_object(config_test)
    print("test environment")
else:
    config.from_object(config_online)
    print("online environment")


def test_get_user_info():
    assert(get_user_info('luyaooo@qq.com') is None)
    print(get_user_info('luyao@qq.com'))


if __name__ == '__main__':
    test_get_user_info()
