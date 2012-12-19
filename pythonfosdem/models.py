# -*- coding: utf-8 -*-
"""
    pythonfosdem.models
    ~~~~~~~~~~~~~~~~~~~

    Models for the project

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime
from pythonfosdem.extensions import db


class CommonMixin(object):
    @property
    def created_on(self):
        return datetime.date(self.created_at.year, self.created_at.month, self.created_at.day)


class Speaker(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    short_bio = db.Column(db.Text, nullable=False)
    twitter = db.Column(db.String(255))
    site = db.Column(db.String(255))
    company = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)


class Talk(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255, convert_unicode=True), nullable=False)
    speaker_id = db.Column(db.Integer, db.ForeignKey('speaker.id'), nullable=False)
    speaker = db.relationship('Speaker', backref=db.backref('talks', lazy='dynamic'))
    description = db.Column(db.Text, nullable=False)
    site = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    approved = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)


class TalkProposal(db.Model, CommonMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(255, convert_unicode=True), nullable=False)
    lastname = db.Column(db.String(255, convert_unicode=True), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255, convert_unicode=True))
    twitter = db.Column(db.String(255))
    site_url = db.Column(db.String(255))
    biography = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(255, convert_unicode=True), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           default=datetime.datetime.utcnow,
                           nullable=False)
