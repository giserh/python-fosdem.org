# -*- coding: utf-8 -*-
"""
    pythonfosdem.bp_general
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements the main interface

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import datetime

from flask import abort
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import current_app
from flask.ext.babel import _
from flask.ext.mail import Message
from flask.ext.security import roles_accepted
from flask.ext.security import login_required
from flask.ext.security import url_for_security
from flask.ext.security.core import current_user
from flask.ext.security.forms import ResetPasswordForm
from flask.ext.security.recoverable import update_password
from flask.ext.security.utils import get_message

from pythonfosdem.extensions import cache
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
from pythonfosdem.forms import SubscribeForm
from pythonfosdem.forms import UserProfileForm
from pythonfosdem.forms import TalkForm
from pythonfosdem.forms import TalkProposalForm
from pythonfosdem.models import Event
from pythonfosdem.models import Subscriber
from pythonfosdem.models import Talk
from pythonfosdem.models import TalkVote
from pythonfosdem.models import User
from pythonfosdem.presenters import UserPresenter
from pythonfosdem.presenters import TalkPresenter
import pythonfosdem.tools

__all__ = ['blueprint']

blueprint = Blueprint('general', __name__, template_folder='templates')


def to_index():
    return redirect(url_for('general.index'))


def convert_to_presenter(iterable, klass):
    for item in iterable:
        yield klass(item)


@blueprint.route('/')
#@cache.cached(timeout=30)
def index():
    scheduler_available = True
    if scheduler_available:
        return redirect(url_for('general.schedule'))

    event = Event.current_event()

    dateline_has_reached = datetime.date.today() >= event.duedate_stop_on
    subscribe_form = SubscribeForm()
    return render_template('general/index.html', 
                           dateline_has_reached=dateline_has_reached,
                           scheduler_available=scheduler_available,
                           subscribe_form=subscribe_form,
                           event=event,
                          )


@blueprint.route('/schedule')
@cache.cached(timeout=30)
def schedule():
    event = Event.current_event()
    talks = list(convert_to_presenter(event.validated_talks, TalkPresenter))
    subscribe_form = SubscribeForm()
    return render_template('general/schedule.html',
                           talks=talks,
                           subscribe_form=subscribe_form)



@blueprint.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash(_('Your profile has been updated !'))
        return redirect(url_for('general.profile'))
    return render_template('general/user_profile.html',
                           user=current_user,
                           form=form)


@blueprint.route('/profile/change-password', methods=['POST', 'GET'])
@login_required
def change_password():
    form = ResetPasswordForm()

    if form.validate_on_submit():
        update_password(current_user, form.password.data)
        flash(*get_message('PASSWORD_RESET'))
        db.session.commit()
        return redirect(url_for('general.profile'))

    return render_template('general/change_password.html',
                           form=form)


@blueprint.route('/u/<int:user_id>')
@blueprint.route('/u/<int:user_id>-<slug>')
def user(user_id, slug=''):
    user = User.query.get_or_404(user_id)
    if user.slug != slug:
        return redirect(url_for('general.user', user_id=user.id, slug=user.slug))
    return render_template('general/user.html', user=UserPresenter(user))

@blueprint.route('/speakers')
def speakers():
    #speakers = User.query.filter(User.talks.isnot(None))       # TODO make it works!
    speakers = set(t.user for t in Talk.query.filter_by(state='validated'))
    return render_template('general/speakers.html', speakers=speakers)


@blueprint.route('/talks/submit', methods=['GET', 'POST'])
@login_required
def talk_submit():
    today = datetime.date.today()
    event = Event.current_event()

    if today > event.duedate_stop_on:
        return render_template('general/closed_talk_proposal.html')

    talk = Talk()
    form = TalkProposalForm(obj=talk)

    if form.validate_on_submit():

        talk = Talk(
            name=form.title.data,
            user=current_user,
            description=form.description.data,
            twitter=form.twitter.data,
            level=form.level.data,
            site=form.site_url.data,
            event=event,
        )

        flash(_('Your proposal will be moderated as soon as possible'))

        msg = pythonfosdem.tools.mail_message(
            _('Thank you for your proposal'),
            recipients=[current_user.email],
            templates={'txt': 'emails/send_thank.txt'},
            values=dict(talk=talk)
        )
        mail.send(msg)
        db.session.add(talk)
        db.session.commit()

        return to_index()
    return render_template('general/talk_proposal.html',
                           current_nav_link='general.index',
                           form=form)



# NOT YET IMPLEMENTED
# @blueprint.route('/about')
# def about_us():
#     return render_template('general/about.html')

# NOT YET IMPLEMENTED
@blueprint.route('/talk_proposals')
@blueprint.route('/talk_proposals/<int:event_id>')
@roles_accepted('admin', 'jury_member', 'jury_president')
def talk_proposals(event_id=None):
    if event_id is None:
        records = Talk.query.join(Talk.user, Talk.event).order_by(Talk.name.asc()).all()
    else:
        records = Talk.query.join(Talk.event).filter(Talk.event_id==event_id).order_by(Talk.name.asc()).all()
    return render_template('general/talk_proposals.html', records=records)


@blueprint.route('/talk/<int:record_id>')
@blueprint.route('/talk/<int:record_id>-<slug>')
def talk_show(record_id, slug=''):
    talk = Talk.query.get_or_404(record_id)
    if talk.slug != slug:
        return redirect(url_for('general.talk_show', record_id=talk.id, slug=talk.slug))
    return render_template('general/talk_show.html', talk=TalkPresenter(talk))


@blueprint.route('/talk/<int:record_id>/edit', methods=['POST', 'GET'])
@roles_accepted('admin')
def talk_edit(record_id):
    talk = Talk.query.get_or_404(record_id)
    form = TalkForm(obj=talk)
    if form.validate_on_submit():
        form.populate_obj(talk)
        db.session.add(talk)
        db.session.commit()
        return redirect(url_for('general.talk_edit'))

    return render_template('general/talk_edit.html', form=form, talk=talk)

    form = UserProfileForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.add(current_user)
        db.session.commit()
        flash(_('Your profile has been updated !'))
        return redirect(url_for('general.profile'))
    return render_template('general/user_profile.html',
                           user=current_user,
                           form=form)


@blueprint.route('/talk/vote', methods=['POST'])
@roles_accepted('jury_member')
def talk_vote():
    if not request.form:
        abort(404)

    record_id = request.form['record_id']
    vote = request.form['vote']
    vote_value = {
        'up': 1,
        'down': -1,
        'none': 0,
    }[vote]

    talk = Talk.query.get_or_404(record_id)

    talk_vote = talk.current_user_vote
    if talk_vote is None:
        # create new one
        talk_vote = TalkVote(user=current_user,
                             talk=talk,
                             value=vote_value)
    else:
        talk_vote.value = vote_value

    db.session.add(talk_vote)
    db.session.commit()

    return jsonify(success=True, record_id=record_id, vote=vote)


@blueprint.route('/talk/change_status', methods=['POST'])
@roles_accepted('jury_president')
def change_status():
    if not request.form:
        abort(404)

    record_id = request.form['record_id']
    state = request.form['vote']

    talk = Talk.query.get_or_404(record_id)

    talk.state = state

    db.session.add(talk)
    db.session.commit()

    return jsonify(success=True, record_id=record_id)


@blueprint.route('/talks/dashboard')
@roles_accepted('jury_member', 'jury_president')
def talks_dashboard():
    event = Event.current_event()
    records = event.talks.all()

    return render_template('general/talks_dashboard.html', records=records)


@blueprint.route('/talks/to_validate')
@roles_accepted('jury_president')
def talks_to_validate():
    event = Event.current_event()
    records = event.talks.all()

    return render_template('general/talks_dashboard.html', records=records)


@blueprint.route('/subscribe', methods=['POST', 'GET'])
def subscribe():
    form = SubscribeForm()

    if form.validate_on_submit():
        email = form.email.data
        sub = Subscriber.add(email)
        db.session.commit()

        unsubscribe_url = url_for('general.unsubscribe', token=sub.unsubscribe_token, _external=True)

        msg = pythonfosdem.tools.mail_message(
            _('Thank you for your subscription to our newsletter'),
            recipients=[email],
            templates={'txt': 'emails/news_subscribe.txt'},
            values=dict(unsubscribe_url=unsubscribe_url)
        )
        mail.send(msg)
        flash('Thank you for your subscription.')
        return redirect(url_for('general.index'))

    return render_template('general/subscribe.html', form=form)

@blueprint.route('/unsubscribe/<token>')
def unsubscribe(token):
    sub = Subscriber.query.filter_by(unsubscribe_token=token).first_or_404()
    sub.active = False
    db.session.add(sub)
    db.session.commit()
    flash("Sorry to hear you don't like us :(")
    return redirect(url_for('general.index'))
