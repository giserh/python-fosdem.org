# -*- encoding: utf-8 -*-
from flask.ext.babel import _
from flask.ext.babel import format_datetime
from flask.ext.babel import format_date
from pythonfosdem.extensions import db
from pythonfosdem.forms import TalkForm


class Address(object):
    def __init__(self, url='', label='', type=None):
        self.url = url
        self.label = label
        self.type = type


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
                           type='twitter',
                           label=label)
        else:
            return Address()

    @property
    def site(self):
        if self.model.site:
            return Address(type='http',
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


class TalkPresenter(Presenter):
    @property
    def schedule(self):
        if self.start_at and self.stop_at:
            return "%s - %s" % (self.start_at.strftime('%H:%M'),
                                self.stop_at.strftime('%H:%M'))
        return ''

    @property
    def type(self):
        return dict(TalkForm.type.kwargs['choices']).get(self.model.type, _('Undefined'))
