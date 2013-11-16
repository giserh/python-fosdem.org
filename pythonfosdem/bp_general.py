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
from flask.ext.security.core import current_user
from flask.ext.security.forms import ResetPasswordForm
from flask.ext.security.recoverable import update_password
from flask.ext.security.utils import get_message

from pythonfosdem.extensions import cache
from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
from pythonfosdem.extensions import security
from pythonfosdem.forms import UserProfileForm
from pythonfosdem.forms import TalkForm
from pythonfosdem.forms import TalkProposalForm
from pythonfosdem.models import Talk
from pythonfosdem.models import TalkVote
from pythonfosdem.models import User
from pythonfosdem.presenters import UserPresenter
from pythonfosdem.presenters import TalkPresenter

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
    scheduler_available = False
    dateline_has_reached = datetime.date.today() >= datetime.date(2013, 12, 1)
    return render_template('general/index.html', 
                           dateline_has_reached=dateline_has_reached,
                           scheduler_available=scheduler_available)


@blueprint.route('/schedule')
@cache.cached(timeout=30)
def schedule():
    talks = Talk.query.filter_by(state='validated').order_by(Talk.start_at.asc())
    talks = convert_to_presenter(talks, TalkPresenter)
    return render_template('general/index.html', talks=talks)



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

    # TODO: Use a record from the database for the date
    if today > datetime.date(2013, 11, 30):
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
            site=form.site_url.data
        )

        flash(_('Your proposal will be moderated as soon as possible'))

        message = Message(_('Thank you for your proposal'),
                          sender=[current_app.config['DEFAULT_EMAIL']],
                          recipients=[current_user.email],
                          bcc=[current_app.config['DEFAULT_EMAIL']],
                          )
        message.body = render_template('emails/send_thank.txt', talk=talk)
        message.html = render_template('emails/send_thank.html', talk=talk)

        mail.send(message)

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
@roles_accepted('admin', 'jury_member', 'jury_president')
def talk_proposals():
    records = Talk.query.join(Talk.user).order_by(User.name.asc()).all()
    return render_template('general/talk_proposals.html', records=records)


@blueprint.route('/talk/<int:record_id>')
@blueprint.route('/talk/<int:record_id>-<slug>')
def talk_show(record_id, slug=''):
    talk = Talk.query.get_or_404(record_id)
    if talk.slug != slug:
        return redirect(url_for('general.talk_show', record_id=talk.id, slug=talk.slug))
    return render_template('general/talk_show.html', talk=talk)


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


@blueprint.route('/talk/validate', methods=['POST'])
@roles_accepted('jury_president')
def talk_validate():
    if not request.form:
        abort(404)

    record_id = request.form['record_id']
    vote = request.form['vote']

    talk = Talk.query.get_or_404(record_id)

    talk.state = 'validated'
    talk.type = vote

    db.session.add(talk)
    db.session.commit()

    return jsonify(success=True, record_id=record_id)


@blueprint.route('/talks/dashboard')
@roles_accepted('jury_member', 'jury_president')
def talks_dashboard():
    result = db.session.execute("""
        SELECT t.id FROM "user" u, talk t
         LEFT OUTER JOIN (SELECT talk_id, value, user_id FROM talk_vote WHERE user_id = :user_id) tv
           ON t.id = tv.talk_id
        WHERE COALESCE(tv.value, 0) = 0
          AND u.id = t.user_id
        ORDER BY u.name
        """,
        {'user_id': current_user.id}
    )
    records = [Talk.query.get(r[0]) for r in result]

    return render_template('general/talks_dashboard.html', records=records)


@blueprint.route('/talks/to_validate')
@roles_accepted('jury_president')
def talks_to_validate():
    result = db.session.execute("""
        SELECT t.id, u.name, u.email, u.twitter, t.name, tv.total
        FROM talk t, 
             (SELECT talk_id, sum(value) total FROM talk_vote GROUP BY talk_id) tv, 
             "user" u 
        WHERE t.id = tv.talk_id 
          AND t.user_id = u.id
          AND tv.total >= 2
          AND t.state NOT IN ('validated')
        ORDER BY tv.total DESC LIMIT :limit
        """,
        {'limit': 16}
    )
    records = [Talk.query.get(r[0]) for r in result]

    return render_template('general/talks_dashboard.html', records=records)
