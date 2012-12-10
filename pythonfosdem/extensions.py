# -*- coding: utf-8 -*-
"""
    pythonfosdem.extensions
    ~~~~~~~~~~~~~~~~~~~~~~~

    Extensions for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.babel import Babel
from flask.ext.bootstrap import Bootstrap
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy

bootstrap = Bootstrap()
babel = Babel()
mail = Mail()
db = SQLAlchemy()
