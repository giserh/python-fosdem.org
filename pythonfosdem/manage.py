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

from pythonfosdem.commands import RunGunicorn
from pythonfosdem.commands import SendInvitationToPreviousSpeakers
from pythonfosdem.commands import SendSpeakerEmails
from pythonfosdem.commands import SendTalkEmails
from pythonfosdem.commands import ShiftSchedule
from pythonfosdem.commands import ShowCurrentEvent
from pythonfosdem.commands import ShowTalkAcceptedTemplate
from pythonfosdem.commands import ShowValidatedTalks

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
    manager.add_command('show_current_event', ShowCurrentEvent())
    manager.add_command('send_talk_emails', SendTalkEmails())
    manager.add_command('send_speaker_emails', SendSpeakerEmails())

    manager.add_command('send_invitation_to_previous_speakers',
                        SendInvitationToPreviousSpeakers())

    manager.add_command('rungunicorn', RunGunicorn())

    manager.add_command('show_validated_talks', ShowValidatedTalks())
    manager.add_command('show_talk_accepted_template', ShowTalkAcceptedTemplate())
    manager.add_command('shift_schedule', ShiftSchedule())

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

    manager.run()
