# -*- coding: utf-8 -*-
import os
import cgitb
import sys

from flask import Flask
from flask import render_template

from flask_babel import _
from flask_mail import Message
from flask_security.core import current_user
from flask_security import user_confirmed
from flask_login import user_logged_in

from pythonfosdem.bp_general import blueprint as bp_general
from pythonfosdem.config import DefaultConfig
from pythonfosdem.admin import configure as configure_admin
from pythonfosdem.extensions import babel
from pythonfosdem.extensions import bootstrap
from pythonfosdem.extensions import cache
from pythonfosdem.extensions import db
from pythonfosdem.extensions import images_set
from pythonfosdem.extensions import mail
from pythonfosdem.extensions import migrate
from pythonfosdem.extensions import security
from pythonfosdem.extensions import maps
from pythonfosdem.forms import TalkForm
from pythonfosdem.forms import LoginForm
from pythonfosdem.forms import RegisterForm
from pythonfosdem.forms import ConfirmRegisterForm
from pythonfosdem.models import Event
from pythonfosdem.models import Role
from pythonfosdem.models import Talk
from pythonfosdem.models import User
from pythonfosdem.models import user_datastore
from pythonfosdem.models import Subscriber

__all__ = ['App', 'create_app']

# TODO: Fix the templates talk_accepted and talk_declined

class App(Flask):
    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', None)
        super(App, self).__init__(*args, **kwargs)

        self.config.from_object(DefaultConfig())

        if config is not None:
            if isinstance(config, basestring):
                self.config.from_pyfile(config)
            else:
                self.config.from_object(config)

        if 'PYTHONFOSDEM_SETTINGS' in os.environ:
            self.config.from_pyfile(os.environ['PYTHONFOSDEM_SETTINGS'])

        self.configure_extensions()
        self.configure_blueprints()
        self.configure_error_handlers()
        self.configure_signals()
        self.configure_templates()

    def configure_blueprints(self):
        self.register_blueprint(bp_general)

    def configure_extensions(self):
        bootstrap.init_app(self)
        babel.init_app(self)
        mail.init_app(self)
        db.init_app(self)
        migrate.init_app(self, db)
        security._state = security.init_app(self,
                                            user_datastore,
                                            register_form=RegisterForm,
                                            confirm_register_form=ConfirmRegisterForm)
        configure_admin(self)
        cache.init_app(self)
        maps.init_app(self)

    def configure_error_handlers(self):
        @self.errorhandler(403)
        def forbidden(error):
            return render_template('errors/403.html'), 403

        @self.errorhandler(404)
        def not_found(error):
            return render_template('errors/404.html'), 404

        @self.errorhandler(500)
        def internal_error(error):
            message = Message(_('[PythonFOSDEM] Error 500'),
                              sender='internal-error@python-fosdem.org',
                              recipients=['stephane@wirtel.be'])
            message.body = render_template('emails/send_error_500.txt',
                                           error=cgitb.text(sys.exc_info()))

            mail.send(message)
            return render_template('errors/500.html'), 500

    def configure_templates(self):

        @self.context_processor
        def inject_user():
            return dict(current_user=current_user)

    def configure_signals(self):

        @user_confirmed.connect_via(self)
        def _auto_subscribe_user(app, user):
            Subscriber.add(user.email)

        @user_logged_in.connect_via(self)
        def user_logged(app, user):
            pass


def create_app(config=None):
    return App(__name__, config=config)
