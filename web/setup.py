# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from rs_admin.version import version_str

setup(
    name='rs-admin',
    version=version_str(),
    description='RadicalSpam Admin Web UI',
    author='Radical-Software Team',
    url='https://github.com/radical-software/rs-admin',
    zip_safe=False,
    license='AGPLv3',
    include_package_data=True,
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=[                 #use python setup.py test for install
        'Flask-Testing',
        'httpretty',
        'nose',
        'coverage',
        'flake8',
    ],
    install_requires=[
        'Flask',
        'arrow',
        'gevent>=1.1.1',
        'python-decouple',
        'pymongo>=3.0.3',
        'Flask-Script',
        'Flask-Moment',
        'Flask-Bootstrap',
        'Flask-BasicAuth',
        'Flask-Mail',
        'redis',
        'psutil',
        'Flask-Assets',
        'jsmin',
        'cssmin',
        'IPy',
        'Flask-Babel',
        #'envoy',      
    ],
    entry_points={
        'console_scripts': [
            'rs-admin = rs_admin.manager:main',
        ],
    },
)
