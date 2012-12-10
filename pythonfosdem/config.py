# -*- coding: utf-8 -*-
"""
    pythonfosdem.models
    ~~~~~~~~~~~~~~~~~~~

    Default configuration for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime
import os


class DefaultConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pythonfosdem.db'
    SQLALCHEMY_ECHO = False
    DEBUG = True

    BABEL_DEFAULT_LOCALE = 'fr_BE'

    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_USE_MINIFIED = True
    SECRET_KEY = '894a4d8c281245609a348cacda11813c'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    UPLOADED_IMAGES_DEST = os.path.join(os.getcwd(), 'uploads')
