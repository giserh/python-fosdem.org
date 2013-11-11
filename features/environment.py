from flask import url_for
from flask.ext.security.core import url_for_security

from pythonfosdem import create_app
from pythonfosdem.tools import reset_db

class TestConfig(object):
    WTF_CSRF_ENABLED = CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

app = create_app(config=TestConfig)

def before_feature(context, feature):
    context.client = app.test_client()

    with app.test_request_context():
        context.login_user_url = url_for_security('login')
        context.talk_submit_url = url_for('general.talk_submit')

        reset_db()