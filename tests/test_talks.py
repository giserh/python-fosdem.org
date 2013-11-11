import re
import unittest2

import pudb

from flask import request
from flask.ext.security import url_for_security
from flask.ext.testing import TestCase
from flask.ext.security.core import current_user
from flask import url_for
from flask import request

from pythonfosdem import App
from pythonfosdem.forms import TalkProposalForm

csrf_token_input = re.compile(
	r'name="csrf_token" type="hidden" value="([0-9a-z#A-Z-\.]*)"'
)

def to_unicode(text):
	if not isinstance(text, unicode):
		return text.decode('utf-8')
	return text

def get_csrf_token(data):
	match = csrf_token_input.search(to_unicode(data))
	assert match
	return match.groups()[0]

#@unittest2.skip("Refactor the code")
class TaskProposalUnitTest(unittest2.TestCase):
    def setUp(self):
        self.app = App(__name__)
        #self.app.config['SECRET_KEY'] = 'deterministic'
        #self.app.config['SESSION_PROTECTION'] = True
        #self.app.config['TESTING'] = True
        print self.app.config['SQLALCHEMY_DATABASE_URI']

    #@unittest2.skip("we skip this test")
    def test_020(self):
        with self.app.test_request_context():
            login_user_url = url_for('security.login')
            talk_submit_url = url_for('general.talk_submit')

        with self.app.test_client() as client:
            values = dict(
                email='stephane@wirtel.be',
                password='secret',
            )

            #response = client.get('/login')
            #print response.data
            #response = client.post('/login', data=values)
            #self.assertTrue(response.status_code == 200)
            #print response.data
            #self.assert_200(user)

            response = client.get(talk_submit_url)
            print response
            csrf_token = get_csrf_token(response.data)

            values = dict(
                title='Evy - Distributed CI',
                description='Description',
                twitter = '@evy',
                site_url = 'http://evy.com',
                level='beginner',
                #csrf_token=csrf_token
            )
            response = client.post(talk_submit_url, data=values)
            print response
