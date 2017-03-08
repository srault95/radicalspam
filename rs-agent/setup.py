# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

setup(
    name='rs-agent',
    version="0.0.1",
    description='',
    author='Stéphane RAULT',
    author_email='stephane.rault@radicalspam.org',
    #url='https://github.com/srault95/rs-smtpd-server', 
    include_package_data=True,
    packages=[
        'rs_agent',
    ],
    install_requires=[
        'six',
        'gevent',
    ],    
    #extras_require=dict(
    #    gevent=['gevent']  
    #),                      
    entry_points={
        'console_scripts': [
            'clamav-cli = rs_agent.clamav_cli:main',
            'sa-cli = rs_agent.sa_cli:main',
        ],
    },    
)
