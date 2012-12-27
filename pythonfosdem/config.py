# -*- coding: utf-8 -*-
"""
    pythonfosdem.config
    ~~~~~~~~~~~~~~~~~~~

    Default configuration for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime
import os


class DefaultConfig(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pythonfosdem.db'
    SQLALCHEMY_ECHO = True
    DEBUG = True

    BABEL_DEFAULT_LOCALE = 'fr_BE'

    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_USE_MINIFIED = True

    SECRET_KEY = '894a4d8c281245609a348cacda11813c'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    UPLOADED_IMAGES_DEST = os.path.join(os.getcwd(), 'uploads')
    DEFAULT_MAIL_SENDER = ('Python @ FOSDEM 2013', 'no-reply@python-fosdem.org')

    #SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'       # FIXME cannot log-in with unencrypted password. check how to configure passlib correclty
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_PASSWORD_SALT = 'pepper'
    SECURITY_EMAIL_SENDER = 'no-reply@python-fosdem.org'
