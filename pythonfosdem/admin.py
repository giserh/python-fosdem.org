# -*- coding: utf-8 -*-
from flask import abort
from flask.ext.admin import AdminIndexView
from flask.ext.security.core import current_user


class AdminView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated()

    def _handle_view(self, name, **kwargs):
        if not self.is_accessible():
            return abort(403)
