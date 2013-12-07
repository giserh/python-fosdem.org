#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    The command line of Python-FOSDEM.org

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from flask.ext.script.commands import ShowUrls
from flask.ext.script import Shell
from flask.ext.migrate import MigrateCommand

from pythonfosdem import create_app
from pythonfosdem.extensions import db

from pythonfosdem.commands import SendTalkEmails
from pythonfosdem.commands import SendSpeakerEmails
from pythonfosdem.commands import SendInvitationToPreviousSpeakers
from pythonfosdem.commands import RunGunicorn

import pythonfosdem.tools
import pythonfosdem.models

def _make_context():
    return dict(db=db, models=pythonfosdem.models)

def main():
    manager = Manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.add_command('db', MigrateCommand)
    manager.add_command('shell', Shell(make_context=_make_context))
    manager.add_command('routes', ShowUrls())
    manager.add_command('send_talk_emails',
                        SendTalkEmails())

    manager.add_command('send_speaker_emails',
                        SendSpeakerEmails())

    manager.add_command('send_invitation_to_previous_speakers',
                        SendInvitationToPreviousSpeakers())

    manager.add_command('rungunicorn', RunGunicorn())

    @manager.command
    def import_xml(filename):
        pythonfosdem.tools.import_xml(filename)

    @manager.command
    def db_create():
        db.create_all()

    @manager.command
    def db_drop():
        db.drop_all()

    @manager.command
    def db_reset():
        pythonfosdem.tools.reset_db()

    @manager.command
    def change_migration():
        import datetime
        from pythonfosdem.models import Talk, Event

        fosdem_2013 = Event.query.filter_by(name='Python FOSDEM 2013').first()
        if not fosdem_2013:
            fosdem_2013 = Event(
                name='Python FOSDEM 2013',
                start_on=datetime.date(2013, 02, 03),
                stop_on=datetime.date(2013, 02, 03),
                active=False
            )
            db.session.add(fosdem_2013)

        fosdem_2014 = Event.query.filter_by(name='Python FOSDEM 2014').first()
        if not fosdem_2014:
            fosdem_2014 = Event(
                name='Python FOSDEM 2014',
                start_on=datetime.date(2014, 02, 01),
                stop_on=datetime.date(2014, 02, 02),
                duedate_start_on=datetime.date(2013, 11, 17),
                duedate_stop_on=datetime.date(2013, 12, 15)
            )
            db.session.add(fosdem_2014)

        for talk in Talk.query.order_by(Talk.id).all():
            if talk.created_on < fosdem_2014.duedate_start_on:
                talk.event = fosdem_2013
            else:
                talk.event = fosdem_2014

            print "%04d" % (talk.id,), talk.created_on, talk.name, talk.start_at, talk.event.id
            db.session.add(talk)

        db.session.commit()

    manager.run()
