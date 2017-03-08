# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

from rs_autoconfig.version import version_str

setup(
    name='rs-autoconfig',
    version=version_str(),
    description='RadicalSpam Auto Config',
    author='Radical-Software Team',
    url='https://github.com/radical-software/autoconfig',
    zip_safe=False,
    license='AGPLv3',
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'six',
        'python-decouple',
        'psutil',
        'pyyaml',
        'tplconfig',
        'plumbum',
    ],
    entry_points={
        'console_scripts': [
            'rs-autoconfig = rs_autoconfig.core:main',
        ],
    },
)
