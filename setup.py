#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='Goodreads',
    version='0.1.1',
    description='A Python wrapper for the goodreads.com api',
    long_description=readme + '\n\n' + history,
    author='Paul Shannon',
    author_email='paul@paulshannon.ca',
    url='https://github.com/paulshannon/python-goodreads',
    packages=[
        'Goodreads',
    ],
    package_dir={'Goodreads': 'goodreads'},
    include_package_data=True,
    install_requires=['oauth2', 'requests', 'lxml'],
    license="BSD",
    zip_safe=False,
    keywords='goodreads',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
)
