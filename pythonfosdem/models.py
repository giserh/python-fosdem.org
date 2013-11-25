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

from flask.ext.security import RoleMixin
from flask.ext.security import SQLAlchemyUserDatastore
from flask.ext.security import UserMixin
from flask.ext.security.core import current_user

from pythonfosdem.extensions import db
from pythonfosdem.extensions import images_set
from pythonfosdem.tools import slugify




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
        return cls.__name__.lower()

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


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, Mixin, RoleMixin):
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    #def __unicode__(self):
    #    return self.name


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

    #def __unicode__(self):
    #    return self.name

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)


class Event(db.Model, Mixin):
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)


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
