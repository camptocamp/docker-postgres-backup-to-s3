#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import pg253

setup(
    name='pg253',
    version='1.0.0',
    packages=find_packages(),
    author="Julien Acroute",
    author_email="julien.acroute@camptocamp.com",
    entry_points = {
        'console_scripts': [
            'backup = pg253.pg253:main',
        ],
    },
    license="Apache 2",
)
