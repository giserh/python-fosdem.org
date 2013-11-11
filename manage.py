#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    The command line of Python-FOSDEM.org

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask import url_for
from flask.ext.babel import _
from flask.ext.mail import Message
from flask.ext.script import Manager
from flask.ext.script.commands import ShowUrls
from pythonfosdem import create_app
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
import pythonfosdem.tools
import pythonfosdem.models
import pythonfosdem.xml_importer
from pythonfosdem.models import Talk
from pythonfosdem.models import User


def mail_message(title, recipients=None, templates=None, values=None):
    assert isinstance(recipients, list)
    assert isinstance(templates, dict)
    assert isinstance(values, dict)

    msg = Message(
        _('[Python-FOSDEM] %s') % title,
        recipients=recipients,
        sender='info@python-fosdem.org',
        bcc=['stephane@wirtel.be']
    )

    if 'txt' in templates:
        msg.body = render_template(templates['txt'], **values)

    return msg

def main():
    manager = Manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)
    manager.add_command('routes', ShowUrls())

    @manager.command
    def show():
        print dir(manager)

    @manager.command
    def send_talk_emails():
        with mail.connect() as conn:
            for talk in Talk.query.filter_by(state='validated'):
                values = {
                    'url_talk': 'http://python-fosdem.org%s' % (url_for('general.talk_show', record_id=talk.id, slug=talk.slug),),
                    'speaker': talk.user.name,
                    'talk_name': talk.name,
                    'talk_description': talk.description,
                    'talk': talk,
                }

                msg = mail_message(
                    _('Your talk has been accepted !'),
                    recipients=[talk.user.email],
                    templates={'txt': 'emails/talk_accepted.txt'},
                    values=values
                )

                conn.send(msg)

    @manager.command
    def send_speaker_emails():
        with mail.connect() as conn:
            for user in User.query.order_by(User.name).all():
                if user.is_speaker:
                    message = Message(_('[Python-FOSDEM] Information and Questions'),
                                      sender='info@python-fosdem.org',
                                      recipients=['stephane@wirtel.be'],
                                      bcc=['stephane@wirtel.be']
                                      )
                    message.body = render_template('emails/speaker_email.txt', user=user)
                    conn.send(message)

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

if __name__ == '__main__':
    main()
