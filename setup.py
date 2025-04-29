#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from setuptools import setup


setup(
    name='utm5ips',
    version='0.1',
    description='Free (unallocated) ip addresses from UTM5 Billing system',
    author='NETCON',
    author_email='support@netcon.team',
    url='https://netcon.team',
    py_modules=['app.py', 'utm5ips/__init__.py', 'utm5ips/interface.py']
)
