# -*- coding: utf-8 -*-
"""
    pythonfosdem.bp_general
    ~~~~~~~~~~~~~~~~~~~~~~~

    Implements the main interface

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask import render_template
from flask import Blueprint
from flask import redirect

from flask import url_for

from pythonfosdem.extensions import db
# from pythonfosdem.models import Speaker
from pythonfosdem.models import TalkProposal
from pythonfosdem.forms import TalkProposalForm

__all__ = ['blueprint']

blueprint = Blueprint('general', __name__, template_folder='templates')


def to_index():
    return redirect(url_for('general.index'))


@blueprint.route('/')
def index():
    form = TalkProposalForm()
    return render_template('general/index.html',
                           current_nav_link='general.index',
                           form=form)


# NOT YET IMPLEMENTED
# @blueprint.route('/speakers')
# def speakers():
#     speakers = Speaker.query.all()
#     return render_template('general/speakers.html', speakers=speakers)


@blueprint.route('/talk_proposal', methods=['GET', 'POST'])
def talk_proposal():
    talkProposal = TalkProposal()
    form = TalkProposalForm(obj=talkProposal)
    if form.validate_on_submit():
        talkProposal = TalkProposal()
        form.populate_obj(talkProposal)

        db.session.add(talkProposal)
        db.session.commit()

        return to_index()
    return render_template('general/talk_proposal.html',
                           current_nav_link='general.talk_proposal',
                           form=form)


# NOT YET IMPLEMENTED
# @blueprint.route('/about')
# def about_us():
#     return render_template('general/about.html')


# NOT YET IMPLEMENTED
# @blueprint.route('/talk_proposals')
# def talk_proposals():
#     records = TalkProposal.query.all()
#     return render_template('general/talk_proposals.html', records=records)
