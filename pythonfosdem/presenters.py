# -*- encoding: utf-8 -*-
# import jinja2
# from flask.ext.babel import _
from pythonfosdem.extensions import db
# from pythonfosdem.structs import Address
from flask.ext.babel import format_datetime
from flask.ext.babel import format_date


class Address(object):
    def __init__(self, url='', label='', is_http=False, is_mail=False, is_none=True, is_twitter=False):
        self.url = url
        self.label = label
        self.is_http = is_http
        self.is_mail = is_mail
        self.is_none = is_none
        self.is_twitter = is_twitter


class Presenter(object):
    def __init__(self, model):
        assert isinstance(model, db.Model)
        self.model = model

    def __getattr__(self, value):
        return getattr(self.model, value)

    @property
    def created_on(self):
        return format_date(self.model.created_on)

    @property
    def created_at(self):
        return format_datetime(self.model.created_at)


class UserPresenter(Presenter):
    @property
    def twitter(self):
        if self.model.twitter:
            if self.model.twitter.startswith('@'):
                twitter_account = self.model.twitter[1:]
                label = self.model.twitter
            else:
                twitter_account = self.model.twitter
                label = '@' + self.model.twitter

            return Address(url='https://twitter.com/%s' % (twitter_account,),
                           is_twitter=True,
                           label=label)
        else:
            return Address()

    @property
    def site(self):
        if self.model.site:
            return Address(is_http=True,
                           url=self.model.site,
                           label=self.model.site)
        else:
            return Address()

    @property
    def urls(self):
        return filter(
            None,
            (getattr(self, address, None)
             for address in 'twitter site'.split())
        )
