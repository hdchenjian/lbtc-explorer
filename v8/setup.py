#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='v8',
    version='0.1',
    url='',
    license='MIT',
    author='Chen Jian',
    author_email='chenjian@reconova.com',
    description='mysql engine',
    packages=find_packages(),
    include_package_data=False,
    zip_safe=False,
    platforms='any',
    classifiers=['Private :: Do Not Upload'],
    install_requires=[
        'arrow==0.8.0',
        'PyMySQL==0.6.2',
        'SQLAlchemy==0.9',
    ],
)
