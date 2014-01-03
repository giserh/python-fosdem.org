# -*- coding: utf-8 -*-
"""
    pythonfosdem.models
    ~~~~~~~~~~~~~~~~~~~

    Models for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime
import hashlib
import uuid

from werkzeug import cached_property

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.event import listen
from sqlalchemy.schema import CheckConstraint

from flask.ext.security import RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security import UserMixin
from flask.ext.security.core import current_user

from pythonfosdem.extensions import db
from pythonfosdem.extensions import images_set
from pythonfosdem.tools import slugify

import inflection


class PrimaryKey(db.Column):
    def __init__(self, *args, **kwargs):
        kwargs.update(type_=db.Integer,
                      primary_key=True)
        super(PrimaryKey, self).__init__(**kwargs)


class MandatoryDateTime(db.Column):
    def __init__(self, *args, **kwargs):
        kwargs.update(type_=db.DateTime,
                      default=datetime.datetime.now,
                      nullable=False)
        super(MandatoryDateTime, self).__init__(**kwargs)


class Mixin(object):
    id = PrimaryKey()
    created_at = MandatoryDateTime()

    @declared_attr
    def __tablename__(cls):
        original_name = cls.__name__
        return inflection.underscore(original_name)

    @property
    def created_on(self):
        return self.created_at.date()

    def __unicode__(self):
        if hasattr(self, 'name'):
            return self.name
        else:
            return "<{name} {id}>".format(name=self.__class__.__name__,
                                          id=self.id)

class ModelData(db.Model, Mixin):
    name = db.Column(db.String(80), unique=True)

    ref_model = db.Column(db.String(80), nullable=False)
    ref_id = db.Column(db.Integer, nullable=False)


class ConfigParameter(db.Model, Mixin):
    name = db.Column(db.String(80), unique=True, nullable=False)

    value_string = db.Column(db.String)
    value_integer = db.Column(db.Integer)
    value_date = db.Column(db.Date)
    value_datetime = db.Column(db.DateTime)

    type = db.Column(db.String)

    @property
    def value(self):
        if self.type == 'string':
            return self.value_string
        if self.type == 'integer':
            return self.value_integer
        if self.type == 'date':
            return self.value_date
        if self.type == 'datetime':
            return self.value_datetime

    @value.setter
    def value(self, value):
        if isinstance(value, datetime.datetime):
            self.type = 'datetime'
            self.value_datetime = value
        if isinstance(value, datetime.date):
            self.type = 'date'
            self.value_date = value
        if isinstance(value, (int, long)):
            self.type = 'integer'
            self.value_integer = value
        if isinstance(value, basestring):
            self.type = 'string'
            self.value_string = value

roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, Mixin, RoleMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, Mixin, UserMixin):
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    biography = db.Column(db.Text)
    twitter = db.Column(db.String(255))
    site = db.Column(db.String(255))
    company = db.Column(db.String(255))
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    photo_path = db.Column(db.String(255))

    @property
    def url(self):
        return images_set.url(self.photo_path)

    talks = db.relationship("Talk",
                            primaryjoin="and_(User.id == Talk.user_id, "
                                        "     Talk.state == 'validated')",
                            #backref=db.backref('user', lazy='joined')
                            )

    @cached_property
    def is_speaker(self):
        return bool(self.talks)

    def gravatar(self, size=None, default='identicon'):
        url = 'http://www.gravatar.com/avatar/{md5}.jpg?d={default}'
        if size is not None:
            url += '&s={size}'
        return url.format(
            md5=hashlib.md5(self.email).hexdigest(),
            default=default,
            size=size
        )

    @cached_property
    def slug(self):
        return slugify(self.name)


# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Event(db.Model, Mixin):
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    start_on = db.Column(db.Date(), nullable=False, default=datetime.date.today)
    stop_on = db.Column(db.Date(), nullable=False, default=datetime.date.today)
    duedate_start_on = db.Column(db.Date())
    duedate_stop_on = db.Column(db.Date())
    active = db.Column(db.Boolean, default=True)
    validated_talks = db.relationship(
        'Talk',
        primaryjoin="and_(Event.id == Talk.event_id, Talk.state == 'validated')",
        order_by="Talk.start_at"
    )


    @staticmethod
    def validate_dates(mapper, connection, event):
        if event.start_on > event.stop_on:
            raise ValueError("The start date is greater than the stop date")

        if event.duedate_stop_on and event.duedate_stop_on > event.start_on:
            raise ValueError("The due date has to be less than the start date")

        if event.duedate_start_on and event.duedate_start_on > event.duedate_stop_on:
            raise ValueError("The due date is greater than the stop date")

    @classmethod
    def current_event(cls):
        return cls.query.filter_by(active=True).order_by(cls.start_on.desc()).limit(1).first()


listen(Event, 'before_insert', Event.validate_dates)
listen(Event, 'before_update', Event.validate_dates)

class Talk(db.Model, Mixin):
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('all_talks', lazy='dynamic'))
    description = db.Column(db.Text, nullable=False)
    site = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    state = db.Column(db.String(16), default='draft')
    start_at = db.Column(db.DateTime())
    stop_at = db.Column(db.DateTime())
    is_backup = db.Column(db.Boolean(), default=False)

    __table_args__ = (
        CheckConstraint('start_at < stop_at'),
    )

    type = db.Column(db.String(16), default='talk')
    level = db.Column(db.String(16), default='beginner')

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    event = db.relationship('Event', backref=db.backref('talks', lazy='dynamic'))

    votes = db.relationship('TalkVote', backref="talk")

    def __init__(self, *args, **kwargs):
        event = kwargs.get('event', kwargs.pop('event_id', None))
        if not event:
            current_event = Event.current_event()
            kwargs['event_id'] = current_event.id
        super(Talk, self).__init__(*args, **kwargs)

    @property
    def points(self):
        return sum(v.value for v in self.votes)

    @property
    def current_user_vote(self):
        for v in self.votes:
            if v.user_id == current_user.id:
                return v
        return None

    @cached_property
    def slug(self):
        return slugify(self.name)


class TalkVote(db.Model, Mixin):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    talk_id = db.Column(db.Integer, db.ForeignKey('talk.id'), nullable=False)

    value = db.Column(db.Integer, nullable=False, default=False)


class Subscriber(db.Model, Mixin):
    email = db.Column(db.String, nullable=True, unique=True)
    active = db.Column(db.Boolean)
    unsubscribe_token = db.Column(db.String,
                                  default=lambda: str(uuid.uuid4()).replace('-', ''),
                                  nullable=False)

    @classmethod
    def add(cls, email):
        sub = cls.query.filter_by(email=email).first()
        if not sub:
            sub = cls(email=email)
        sub.active = True
        db.session.add(sub)
        return sub
