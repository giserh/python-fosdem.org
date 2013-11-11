import unittest2

# from flask.ext.testing import TestCase

from pythonfosdem import create_app
from pythonfosdem.tools import reset_db

class TestConfig(object):
    WTF_CSRF_ENABLED = CSRF_ENABLED = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class PFTestCase(unittest2.TestCase):
    def setUp(self):
        self.app = create_app(config=TestConfig())
        with self.app.test_request_context():
            reset_db()
