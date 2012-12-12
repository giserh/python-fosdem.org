# -*- coding: utf-8 -*-
"""
    setup.py
    ~~~~~~~~

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from setuptools import setup
from setuptools import find_packages

setup(
    name='PythonFOSDEM',
    version='0.1dev',
    author='Stephane Wirtel',
    author_email='stephane@wirtel.be',
    url='http://github.com/matrixise/python-fosdem.org',
    license='BSD',
    packages=find_packages(),
    install_requires=[
        'Flask',
        'Flask-Babel',
        'Flask-Bootstrap',
        'Flask-Mail',
        'Flask-Script',
        'Flask-Uploads',
        'Flask-WTF',
        'Flask-SQLAlchemy',
        'gunicorn',
        'psycopg2',
    ],
    include_package_data=True,
)
