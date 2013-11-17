import os
import operator

from werkzeug.contrib.fixers import ProxyFix

from gunicorn.app.base import Application as BaseApplication
from gunicorn.config import Config

from flask import url_for
from flask.ext.babel import _
from flask.ext.script.commands import Command
from flask.ext.script.commands import Option
from pythonfosdem.extensions import mail
from pythonfosdem.models import Talk
from pythonfosdem.models import User
from pythonfosdem.tools import mail_message
from pythonfosdem.tools import count_workers




def external_url_for(endpoint, **kwargs):
    kwargs.update(_external=True)
    return url_for(endpoint, **kwargs)


class SendTalkEmails(Command):
    def run(self):
        with mail.connect() as conn:
            for talk in Talk.query.filter_by(state='validated'):
                values = {
                    'url_talk': external_url_for('general.talk_show',
                                                 record_id=talk.id,
                                                 slug=talk.slug),
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


class SendSpeakerEmails(Command):
    def run(self):
        with mail.connect() as conn:
            for user in User.query.order_by(User.name).all():
                if not user.is_speaker:
                    continue
                msg = mail_message(
                    _('Information and Questions'),
                    recipients=[user.email],
                    templates={'txt': 'emails/speaker_email.txt'},
                    values=dict(user=user)
                )
                conn.send(msg)


class SendInvitationToPreviousSpeakers(Command):
    def run(self):
        with mail.connect() as conn:
            users = set(talk.user for talk in Talk.query.all())
            sorted_users = sorted(users, key=operator.attrgetter('name'))
            for user in sorted_users:
                print user.name, user.email
                msg = mail_message(
                    _('Call For Proposals'),
                    recipients=[user.email],
                    templates={'txt': 'emails/cfp_invitation.txt'},
                    values=dict(user=user)
                )
                conn.send(msg)


class RunGunicorn(Command):
    def __init__(self, host='127.0.0.1', port=5000):
        self.port = port
        self.host = host
        self.pidfile = os.path.join('/', 'tmp', 'pythonfosdem.pid')
        self.workers = count_workers()

    def get_options(self):
        options = (
            Option('--debug',
                   action='store_true',
                   dest='use_debug',
                   default=False),
            Option('-t', '--host',
                   dest='host',
                   default=self.host),
            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port),
            Option('--pidfile',
                   dest='pidfile',
                   default=self.pidfile),
            Option('--workers',
                   dest='workers',
                   type=int,
                   default=self.workers)
        )
        return options

    def handle(self, app, use_debug, host, port, pidfile, workers):
        # We fix a bug when we use a reverse proxy

        options = {
            'bind': '%s:%s' % (host, port),
            'workers': workers,
            'pidfile': pidfile,
        }

        class GunicornApplication(BaseApplication):
            def __init__(self, application, options=None):
                if options is None:
                    options = {}

                self.application = app
                self.prog = None
                self.usage = None
                self.callable = None
                self.options = options
                self.do_load_config()

            def load_config(self):
                self.cfg = Config(self.usage, prog=self.prog)
                # optional settings from apps
                cfg = self.init(None, [], [])

                # Load up the any app specific configuration
                if cfg and cfg is not None:
                    for k, v in cfg.items():
                        self.cfg.set(k.lower(), v)

            def init(self, parser, opts, args):
                config = dict(
                    (key, value)
                    for key, value in map(lambda item: (item[0].lower(), item[1]), self.options.iteritems())
                    if key in self.cfg.settings and value is not None
                )
                return config

            def load(self):
                self.application.wsgi_app = ProxyFix(self.application.wsgi_app)
                return self.application

        GunicornApplication(app, options).run()
