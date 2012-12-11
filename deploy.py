# -*- coding: utf-8 -*-
"""
    deploy.py
    ~~~~~~~~~

    :copyright: (c) 2012 by Stephane Wirtel <stephane@wirtel.be>
"""

from pythonfosdem import create_app
from pythonfosdem.config import DefaultConfig
from werkzeug.contrib.fixers import ProxyFix as ProxyFixMiddleware

__app__ = ['application']


# gunicorn -c conf/gunicorn.conf deploy:application
application = create_app(DefaultConfig)
application.wsgi_app = ProxyFixMiddleware(application.wsgi_app)

