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
from flask.ext.migrate import MigrateCommand

from pythonfosdem import create_app
from pythonfosdem.extensions import db

from pythonfosdem.commands import SendTalkEmails
from pythonfosdem.commands import SendSpeakerEmails
from pythonfosdem.commands import SendInvitationToPreviousSpeakers
from pythonfosdem.commands import RunGunicorn

import pythonfosdem.tools
import pythonfosdem.models

def main():
    manager = Manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.add_command('db', MigrateCommand)
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

    manager.run()
