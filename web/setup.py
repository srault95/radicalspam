# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from rs_admin.version import version_str

setup(
    name='rs-admin',
    version=version_str(),
    description='RadicalSpam Admin Web UI',
    author='Radical-Software Team',
    url='https://github.com/radical-software/radicalspam',
    zip_safe=False,
    license='AGPLv3',
    include_package_data=True,
    packages=find_packages(),
    test_suite='nose.collector',
    tests_require=[
      'nose',
    ],
    entry_points={
        'console_scripts': [
            'rs-admin = rs_admin.manager:main',
        ],
    },
)
