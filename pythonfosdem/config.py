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
    DEFAULT_EMAIL = 'info@python-fosdem.org'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///pythonfosdem.db'
    SQLALCHEMY_ECHO = True
    DEBUG = True
    TESTING = True
    LOGIN_DISABLED = False
    CACHE_TYPE = 'simple'

    BABEL_DEFAULT_LOCALE = 'fr_BE'

    BOOTSTRAP_USE_CDN = True
    BOOTSTRAP_USE_MINIFIED = True

    SECRET_KEY = '894a4d8c281245609a348cacda11813c'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=1)
    UPLOADED_IMAGES_DEST = os.path.join(os.getcwd(), 'uploads')
    MAIL_DEFAULT_SENDER = ('Python @ FOSDEM', DEFAULT_EMAIL)

    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'       # FIXME cannot log-in with unencrypted password. check how to configure passlib correclty
    #SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_PASSWORD_SALT = 'pepper'

    SECURITY_EMAIL_SENDER = DEFAULT_EMAIL

    # Don't comment this line SECURITY_RECOVERABLE because
    # we can have an error with securitu.forgot_password
    SECURITY_RECOVERABLE = True
    SECURITY_REGISTERABLE = True

    MAIL_PORT = 10025
    MAIL_DEFAULT_SUFFIX = '[Python-FOSDEM 2014]'
