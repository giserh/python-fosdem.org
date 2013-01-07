# -*- coding: utf-8 -*-
import os
import cgitb
import sys

from flask import Flask
from flask import render_template

from flask.ext.babel import _
from flask.ext.mail import Message
from flask.ext.security.core import current_user
from flask.ext.uploads import configure_uploads

from pythonfosdem.bp_general import blueprint as bp_general
from pythonfosdem.config import DefaultConfig
from pythonfosdem.extensions import admin
from pythonfosdem.extensions import babel
from pythonfosdem.extensions import bootstrap
from pythonfosdem.extensions import cache
from pythonfosdem.extensions import db
from pythonfosdem.extensions import images_set
from pythonfosdem.extensions import mail
from pythonfosdem.extensions import security

from pythonfosdem.models import user_datastore

__all__ = ['App', 'create_app']


class App(Flask):
    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', None)

        Flask.__init__(self, *args, **kwargs)

        self.config.from_object(DefaultConfig())

        if config is not None:
            if isinstance(config, basestring):
                self.config.from_pyfile(config)
            else:
                self.config.from_object(config)

        if 'PYTHONFOSDEM_SETTINGS' in os.environ:
            self.config.from_pyfile(os.environ['PYTHONFOSDEM_SETTINGS'])

        self.configure_blueprints()
        self.configure_extensions()
        self.configure_error_handlers()
        self.configure_templates()

    def configure_blueprints(self):
        self.register_blueprint(bp_general)

    def configure_extensions(self):
        bootstrap.init_app(self)
        babel.init_app(self)
        mail.init_app(self)
        db.init_app(self)
        security.init_app(self, user_datastore)
        configure_uploads(self, (images_set,))
        self.configure_admin()
        cache.init_app(self)

    def configure_admin(self):
        admin.init_app(self)
        from flask.ext.admin.contrib.sqlamodel import ModelView
        from flask.ext.wtf import SelectField
        from pythonfosdem.models import Talk
        from pythonfosdem.models import User
        from pythonfosdem.models import Role
        from pythonfosdem.models import Event

        from pythonfosdem.forms import TalkForm

        class TalkModelView(ModelView):
            # column_list = ('user',)
              # a column.$
            # column_sortable_list = ('name', ('user', User.username), 'date')

            # Rename 'title' columns to 'Post Title' in list view$
            column_labels = dict(name='Title')

            column_searchable_list = ('name',)  # , User.username)

            column_filters = ('name',) 
                              #filters.FilterLike(Post.title, 'Fixed Title', options=(('test1', 'Test 1'), ('test2', 'Test 2'))))

            column_exclude_list = ('description',)
            form_overrides = dict(state=SelectField, type=SelectField)
            form_args = dict(
                # Pass the choices to the `SelectField`
                state=dict(choices=TalkForm.state.kwargs['choices']),
                type=dict(choices=TalkForm.type.kwargs['choices']),
            )

            def __init__(self, session):
                # You can pass name and other parameters if you want to
                super(TalkModelView, self).__init__(Talk, session)

        admin.add_view(TalkModelView(db.session))

        class UserModelView(ModelView):
            inline_models = (Talk,)
            column_list = ('name', 'email', 'created_at', 'is_speaker',)
            column_sortable_list = ('email', 'name',)
            # can_delete = False

            def __init__(self, session):
                # You can pass name and other parameters if you want to
                super(UserModelView, self).__init__(User, session)

        admin.add_view(UserModelView(db.session))

        class RoleModelView(ModelView):
            column_list = ('name', )
            column_sortable_list = ('name',)
            # can_delete = False

            def __init__(self, session):
                # You can pass name and other parameters if you want to
                super(RoleModelView, self).__init__(Role, session)

        admin.add_view(RoleModelView(db.session))

        class EventModelView(ModelView):
            column_list = ('name', )
            column_sortable_list = ('name',)
            # can_delete = False

            def __init__(self, session):
                # You can pass name and other parameters if you want to
                super(EventModelView, self).__init__(Event, session)

        admin.add_view(EventModelView(db.session))

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
            message.body = render_template('emails/send_error_500.txt', error=cgitb.text(sys.exc_info()))

            mail.send(message)
            return render_template('errors/500.html'), 500

    def configure_templates(self):
        @self.context_processor
        def inject_user():
            return dict(current_user=current_user)


def create_app(config=None):
    return App(__name__, config=config)
