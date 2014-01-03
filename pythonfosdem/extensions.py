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
from flask.ext.cache import Cache
from flask.ext.mail import Mail
from flask.ext.migrate import Migrate
from flask.ext.security import Security
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.uploads import IMAGES
from flask.ext.uploads import UploadSet

bootstrap = Bootstrap()
babel = Babel()
mail = Mail()
security = Security()
db = SQLAlchemy()
images_set = UploadSet('images', IMAGES)
cache = Cache()
migrate = Migrate()
