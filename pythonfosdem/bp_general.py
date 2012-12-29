# -*- coding: utf-8 -*-
"""
    pythonfosdem.bp_general
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements the main interface

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask import abort
from flask import Blueprint
from flask import flash
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask.ext.babel import _
from flask.ext.mail import Message
from flask.ext.security import roles_accepted, login_required
from flask.ext.security.core import current_user

from pythonfosdem.extensions import db
from pythonfosdem.extensions import mail
from pythonfosdem.models import Talk
from pythonfosdem.models import TalkProposal
from pythonfosdem.models import TalkVote
from pythonfosdem.models import User
from pythonfosdem.forms import TalkProposalForm
from pythonfosdem.forms import UserProfileForm

__all__ = ['blueprint']

blueprint = Blueprint('general', __name__, template_folder='templates')


def to_index():
    return redirect(url_for('general.index'))


@blueprint.route('/')
def index():
    # return redirect(url_for('general.talk_proposal'))
    return render_template('general/index.html')


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

@blueprint.route('/speakers')
def speakers():
    #speakers = User.query.filter(User.talks.isnot(None))       # TODO make it works!
    speakers = set(t.user for t in Talk.query.filter_by(state='validated'))
    return render_template('general/speakers.html', speakers=speakers)


@blueprint.route('/talk_proposal')
def talk_proposal():
    return render_template('general/closed_talk_proposal.html')


#@blueprint.route('/talk_proposal', methods=['GET', 'POST'])
def open_talk_proposal():
    talkProposal = TalkProposal()
    form = TalkProposalForm(obj=talkProposal)
    if form.validate_on_submit():
        talkProposal = TalkProposal()
        form.populate_obj(talkProposal)

        flash(_('Your proposal will be moderated as soon as possible'), 'info')

        message = Message(_('Thank you for your proposal'),
                          recipients=[talkProposal.email],
                          bcc=['stephane@wirtel.be']
                          )
        message.body = render_template('emails/send_thank.txt', talk=talkProposal)
        message.html = render_template('emails/send_thank.html', talk=talkProposal)

        mail.send(message)

        db.session.add(talkProposal)
        db.session.commit()

        return to_index()
    return render_template('general/talk_proposal.html',
                           form=form)


# NOT YET IMPLEMENTED
# @blueprint.route('/about')
# def about_us():
#     return render_template('general/about.html')


# NOT YET IMPLEMENTED
@blueprint.route('/talk_proposals')
@roles_accepted('admin', 'jury_member')
def talk_proposals():
    records = Talk.query.filter_by(state='draft').join(Talk.user).order_by(User.name.asc()).all()
    # records = TalkProposal.query.all()
    return render_template('general/talk_proposals.html', records=records)


@blueprint.route('/talk/<int:record_id>')
@roles_accepted('admin', 'jury_member')
def talk_show(record_id):
    talk = Talk.query.get_or_404(record_id)
    return render_template('general/talk_show.html', talk=talk)


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
