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

from werkzeug import cached_property

from flask.ext.security import RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security import UserMixin
from flask.ext.security.core import current_user

from pythonfosdem.extensions import db
from pythonfosdem.extensions import images_set
from pythonfosdem.tools import slugify


class CommonMixin(object):
    @property
    def created_on(self):
        return datetime.date(self.created_at.year, self.created_at.month, self.created_at.day)


class ModelData(db.Model, CommonMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)

    ref_model = db.Column(db.String(80), nullable=False)
    ref_id = db.Column(db.Integer, nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)


roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin, CommonMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)

    def __unicode__(self):
        return self.name


class User(db.Model, UserMixin, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    created_at = db.Column(db.DateTime(), default=datetime.datetime.now, nullable=False)
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
        return url.format(md5=hashlib.md5(self.email).hexdigest(), default=default, size=size)

    @cached_property
    def slug(self):
        return slugify(self.name)

    def __unicode__(self):
        return self.name

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Event(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)


class Talk(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('all_talks', lazy='dynamic'))
    description = db.Column(db.Text, nullable=False)
    site = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    state = db.Column(db.String(16), default='draft')
    created_at = db.Column(db.DateTime(),
                           default=datetime.datetime.now,
                           nullable=False)
    start_at = db.Column(db.DateTime())
    stop_at = db.Column(db.DateTime())

    type = db.Column(db.String(16), default='talk')
    level = db.Column(db.String(16), default='beginner')
    
    votes = db.relationship('TalkVote', backref="talk")

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


class TalkVote(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(),
                           default=datetime.datetime.now,
                           nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    talk_id = db.Column(db.Integer, db.ForeignKey('talk.id'), nullable=False)

    value = db.Column(db.Integer, nullable=False, default=False)
