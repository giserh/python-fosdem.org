
# from flask import request
from flask.ext.security.core import current_user
from flask import url_for

# from pythonfosdem.forms import TalkProposalForm

from .common import PFTestCase

class TaskProposalUnitTest(PFTestCase):
    def test_020(self):
        with self.app.test_request_context():
            login_user_url = url_for('security.login')
            talk_submit_url = url_for('general.talk_submit')

        with self.app.test_client() as client:
            values = dict(
                email='stephane@wirtel.be',
                password='secret',
            )

            response = client.post(login_user_url, data=values, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            # print response.data
            #self.assert_200(user)

            self.assertTrue(current_user.is_authenticated())

            values = dict(
                title='Evy - Distributed CI',
                description='Description',
                twitter='@evy',
                site_url='http://evy.com',
                level='beginner',
            )
            response = client.post(talk_submit_url, data=values, follow_redirects=True)
            # print response.data
            self.assertEqual(response.status_code, 200)
