# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2012 by Stephane Wirtel.
    :copyright: (c) 2012 by Christophe Simonis.
    :license: BSD, see LICENSE for more details.
"""
import os
from setuptools import setup
from setuptools import find_packages

HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, 'pip-requirements.txt')) as fp:
    reqs = fp.readlines()

setup(
    name='PythonFOSDEM',
    version='0.1dev',
    author='Stephane Wirtel',
    author_email='stephane@wirtel.be',
    url='http://github.com/matrixise/python-fosdem.org',
    license='BSD',
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
)
