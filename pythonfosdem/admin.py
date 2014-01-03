# -*- coding: utf-8 -*-
from flask import abort
from flask_admin import Admin
from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView as BaseModelView
from flask_security.core import current_user
from wtforms.fields import SelectField
from pythonfosdem.forms import TalkForm

from pythonfosdem.models import Role, Event, Talk, User
from pythonfosdem.extensions import db

class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')

class ModelView(BaseModelView):
    page_size = 50

    def is_accessible(self):
        return current_user.has_role('admin')

class EventModelView(ModelView):
    column_list = ('name', 'start_on', 'stop_on')
    form_columns = ('name', 'start_on', 'stop_on', 'duedate_start_on', 'duedate_stop_on', 'active')

class TalkModelView(ModelView):
    form_widget_args = {
        'name': {
            'class': 'span8',
        },
        'description': {
            'rows': 12,
            'class': 'span8',
        },
        'site': {
            'class': 'span8',
        }
    }

    list_template = 'admin/talk_list.html'
    column_list = (
        'name', 'start_at', 'user.name', 'event.name', 'level',
        'type', 'state'
    )
      # a column.$
    column_sortable_list = (('name', Talk.name), ('user', User.name), 'level', 'state')

    # Rename 'title' columns to 'Post Title' in list view$
    column_labels = {
        'name':'Title',
        'user.name': 'User',
        'event.name': 'Event'
    }

    column_searchable_list = ('name', 'state', User.name, Event.name)

    column_filters = (
        'name', 'level', 'state', 'type', 'event.name',
        'is_backup', 'start_at'
    )

    form_columns = (
        'name', 'description', 'user', 'event', 'site', 'twitter',
        'is_backup', 'state', 'type', 'level', 'start_at', 'stop_at'
    )
    form_overrides = dict(
        state=SelectField,
        type=SelectField,
        level=SelectField
    )

    form_args = dict(
        # Pass the choices to the `SelectField`
        state=dict(choices=TalkForm.state.kwargs['choices']),
        type=dict(choices=TalkForm.type.kwargs['choices']),
        level=dict(choices=TalkForm.level.kwargs['choices'])
    )

class UserModelView(ModelView):
    inline_models = (Talk,)
    column_list = ('name', 'email', 'created_at', 'is_speaker',)
    column_sortable_list = ('email', 'name',)


class RoleModelView(ModelView):
    column_list = ('name', )
    column_sortable_list = ('name',)


def configure(app):
    admin = Admin(app, 'Python @ FOSDEM', index_view=AdminView())
    admin.add_view(RoleModelView(Role, db.session))
    admin.add_view(EventModelView(Event, db.session))
    admin.add_view(TalkModelView(Talk, db.session))
    admin.add_view(UserModelView(User, db.session))
    from flask_admin.base import MenuLink
    admin.add_link(MenuLink("Site", endpoint='general.index'))

