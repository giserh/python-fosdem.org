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
from flask.ext.security import Security
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import UploadSet
from flask.ext.uploads import IMAGES
from flask.ext.admin import Admin
from pythonfosdem.admin import AdminView

bootstrap = Bootstrap()
babel = Babel()
mail = Mail()
security = Security()
db = SQLAlchemy()
images_set = UploadSet('images', IMAGES)
admin = Admin(name='Python @ FOSDEM', index_view=AdminView())
