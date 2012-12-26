#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~

    The command line of Python-FOSDEM.org

    :copyright: (c) 2012 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
from flask.ext.script import Manager
from pythonfosdem import create_app
from pythonfosdem.extensions import db
from pythonfosdem.models import user_datastore
import pythonfosdem.models
import pythonfosdem.xml_importer


def main():
    manager = Manager(create_app)

    @manager.command
    def import_data(filename):
        from collections import OrderedDict

        with open(filename, 'r') as fp:
            records = OrderedDict()
            pythonfosdem.xml_importer.parse(records, fp)

            # from pprint import pprint as pp
            # pp(dict((xml_id, record.to_struct())
            #    for xml_id, record in records.iteritems()))

            for xml_id, record in records.iteritems():
                ModelClass = getattr(pythonfosdem.models, record.model)
                instance = ModelClass(**record.fields)
                db.session.add(instance)

            db.session.commit()

    @manager.command
    def db_populate():
        admin = user_datastore.create_role(name='admin')
        speaker = user_datastore.create_role(name='speaker')     # noqa
        jury_member = user_datastore.create_role(name='jury_member')

        stephane = user_datastore.create_user(name=u'Stéphane Wirtel',
                                              password='1234',
                                              email='stephane@wirtel.be',
                                              active=True,
                                              )

        christophe = user_datastore.create_user(name='Christophe Simonis',
                                                password='1234',
                                                email='christophe@simonis.kn.gl',
                                                active=True,
                                                )

        tarek = user_datastore.create_user(name='Tarek Ziade',
                                           password='1234',
                                           email='tarek@ziade.org',
                                           active=True)

        ludovic = user_datastore.create_user(name='Ludovic Gasc',
                                             password='1234',
                                             email='gmludo@gmail.com',
                                             active=True)

        # TODO create Ludo and Tarek

        user_datastore.add_role_to_user(stephane, admin)
        user_datastore.add_role_to_user(christophe, admin)

        user_datastore.add_role_to_user(stephane, jury_member)
        user_datastore.add_role_to_user(christophe, jury_member)
        user_datastore.add_role_to_user(tarek, jury_member)
        user_datastore.add_role_to_user(ludovic, jury_member)

        db.session.commit()

    @manager.command
    def db_create():
        db.create_all()

    @manager.command
    def db_drop():
        db.drop_all()

    manager.run()

if __name__ == '__main__':
    main()
