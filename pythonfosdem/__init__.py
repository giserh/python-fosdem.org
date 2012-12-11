# -*- coding: utf-8 -*-
from flask import Flask

from pythonfosdem.bp_general import blueprint as bp_general
from pythonfosdem.config import DefaultConfig
from pythonfosdem.extensions import babel
from pythonfosdem.extensions import bootstrap
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail

__all__ = ['App', 'create_app']


class App(Flask):
    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', None)

        Flask.__init__(self, *args, **kwargs)

        self.config.from_object(DefaultConfig())

        if config is None:
            self.config.from_object(config)

        self.configure_blueprints()
        self.configure_extensions()

    def configure_blueprints(self):
        self.register_blueprint(bp_general)

    def configure_extensions(self):
        bootstrap.init_app(self)
        babel.init_app(self)
        mail.init_app(self)
        db.init_app(self)


def create_app(config=None):
    return App(__name__, config=config)
