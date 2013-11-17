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
from pythonfosdem import release

HERE = os.path.dirname(__file__)

with open(os.path.join(HERE, 'pip-requirements.txt')) as fp:
    reqs = [x.strip() for x in fp.readlines()]

setup(
    name=release.name,
    version=release.version,
    author=release.author,
    author_email=release.author_email,
    url=release.url,
    license='BSD',
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    test_requires = [
        'nose2',
    ],
    test_suite='nose2.collector',
    entry_points="""
    [console_scripts]
    python-fosdem = pythonfosdem.manage:main
    """
)
