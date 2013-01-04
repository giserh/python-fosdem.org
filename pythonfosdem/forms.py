# -*- coding: utf-8 -*-
"""
    pythonfosdem.forms
    ~~~~~~~~~~~~~~~~~~

    Implements several HTML forms

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import flask.ext.wtf
from flask.ext.wtf import Form
from flask.ext.wtf import Length
from flask.ext.wtf import Required
from flask.ext.wtf import BooleanField
from flask.ext.wtf import SelectField
from flask.ext.wtf import SubmitField
from flask.ext.wtf import TextAreaField
from flask.ext.wtf import TextField
from flask.ext.wtf.html5 import EmailField
from flask.ext.wtf.html5 import URLField
from flask.ext.babel import lazy_gettext
from wtforms.widgets import Input
from wtforms.validators import ValidationError


# Fucking Workaround, I don't like THAT :/
# WTForms does use keyword arguments the constructor of the fields,
# it's a limitation if you want to add a custom flag
old_init = flask.ext.wtf.Field.__init__


def new_init(self, *args, **kwargs):
    self.placeholder = kwargs.pop('placeholder', False)
    return old_init(self, *args, **kwargs)


flask.ext.wtf.Field.__init__ = new_init


class TwitterInput(Input):
    input_type = 'text'


class TwitterField(TextField):
    widget = TwitterInput()

    def pre_validate(self, form):
        if not self.data.startswith('@'):
            raise ValidationError(self.gettext('Not a valid Twitter account'))

        return super(TwitterField, self).pre_validate(form)


class TalkProposalForm(Form):
    firstname = TextField(
        lazy_gettext(u'Firstname'),
        validators=[Required(), Length(min=4, max=128)],
        placeholder=lazy_gettext(u'Your firstname'),
    )

    lastname = TextField(
        lazy_gettext(u'Lastname'),
        validators=[Required(), Length(min=4, max=128)],
        placeholder=lazy_gettext(u'Your lastname')
    )

    email = EmailField(
        lazy_gettext(u'Email'),
        validators=[Required(), Length(min=4, max=128)],
        placeholder=lazy_gettext(u'Your email')
    )

    company = TextField(
        lazy_gettext(u'Company / Organization'),
        validators=[Length(min=4, max=128)],
        placeholder=lazy_gettext(u'Your company or organization')
    )

    twitter = TwitterField(
        lazy_gettext(u'Twitter'),
        validators=[Length(min=4, max=128)],
        placeholder=lazy_gettext(u'@twitter_account')
    )

    site_url = URLField(
        lazy_gettext(u'Site'),
        validators=[Length(min=4, max=128)],
        description=lazy_gettext(u'Your website or this one of the project'),
        placeholder=lazy_gettext(u'http://project_url')
    )

    biography = TextAreaField(
        lazy_gettext(u'Biography'),
        validators=[Required()],
        placeholder=lazy_gettext(u'Could you add some lines about yourself?')
    )

    title = TextField(
        lazy_gettext(u'Title'),
        validators=[Required(), Length(min=4, max=128)],
        placeholder=lazy_gettext(u'The title of your presentation')
    )

    description = TextAreaField(
        lazy_gettext(u'Description'),
        validators=[Required()],
        placeholder=lazy_gettext(u'Give a description of your talk')
    )

    submit = SubmitField(lazy_gettext(u'Submit Your Talk'))


class UserProfileForm(Form):
    name = TextField(
        lazy_gettext(u'Name'),
        validators=[Required(), Length(min=4, max=255)],
        placeholder=lazy_gettext(u'Your Name'),
    )

    twitter = TwitterField(
        lazy_gettext(u'Twitter'),
        validators=[Length(min=4, max=128)],
        placeholder=lazy_gettext(u'@twitter_account')
    )

    site = URLField(
        lazy_gettext(u'Site'),
        validators=[Length(min=4, max=255)],
        description=lazy_gettext(u'Your website'),
        placeholder=lazy_gettext(u'http://project_url')
    )

    company = TextField(
        lazy_gettext(u'Company / Organization'),
        validators=[Length(min=4, max=128)],
        placeholder=lazy_gettext(u'Your company or organization')
    )

    biography = TextAreaField(
        lazy_gettext(u'Biography'),
        validators=[Required()],
        placeholder=lazy_gettext(u'Could you add some lines about yourself?')
    )

    submit = SubmitField(lazy_gettext(u'Save'))


class TalkForm(Form):
    name = TextField(lazy_gettext(u'Name'),
                     validators=[Required(), Length(min=4, max=128)],
                     description=lazy_gettext(u'The title of the name'))
    description = TextAreaField(
        lazy_gettext(u'Description'),
        validators=[Required()],
        placeholder=lazy_gettext(u'Could you give some lines about this Talk ?')
    )

    site = URLField(
        lazy_gettext(u'Site'),
        validators=[Length(min=4, max=255)],
        description=lazy_gettext(u'Your website'),
        placeholder=lazy_gettext(u'http://project_url')
    )

    twitter = TwitterField(
        lazy_gettext(u'Twitter'),
        validators=[Length(min=4, max=128)],
        placeholder=lazy_gettext(u'@twitter_account')
    )

    approved = BooleanField(lazy_gettext(u'Approved'),
                            description=lazy_gettext(u'Do you confirm this talk is approved'))

    state = SelectField(
        'State',
        choices=[
            ('draft', lazy_gettext(u'Draft')),
            ('validated', lazy_gettext(u'Validated')),
            ('declined', lazy_gettext(u'Declined')),
            ('canceled', lazy_gettext(u'Canceled')),
        ],
        validators=[Required()]
    )

    type = SelectField(
        'Type',
        choices=[
            ('talk', lazy_gettext(u'Talk')),
            ('lightning_talk', lazy_gettext(u'Lightning Talk')),
        ],
        validators=[Required()]
    )

    # start_at = db.Column(db.DateTime(timezone=True))
    # stop_at = db.Column(db.DateTime(timezone=True))

    # type = db.Column(db.String(16), default='talk')

    submit = SubmitField(lazy_gettext(u'Save'))
