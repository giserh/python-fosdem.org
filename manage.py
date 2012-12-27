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
import pythonfosdem.tools
import pythonfosdem.models
import pythonfosdem.xml_importer


def main():
    manager = Manager(create_app)
    manager.add_option('-c', '--config', dest='config', required=False)

    @manager.command
    def import_xml(filename):
        with open(filename, 'r') as fp:
            xml_records = pythonfosdem.xml_importer.parse(fp)

            for xml_id, xml_record in xml_records.iteritems():
                instance, proxy = pythonfosdem.tools.create_or_update(xml_record.model, xml_id)
                instance_is_new = instance.id is None

                for field_name, field_value in xml_record.fields.iteritems():
                    current_field = getattr(instance, field_name)

                    if pythonfosdem.tools.is_relationship(proxy, field_name):
                        for nested_xml_id in xml_record.fields[field_name].split(','):
                            operator = '+'
                            if nested_xml_id[0] in ('+', '-'):
                                operator, nested_xml_id = nested_xml_id[0], nested_xml_id[1:]

                            ref_model, ref_id, record = pythonfosdem.tools.get_xml_id_or_raise(nested_xml_id)

                            if operator == '-':
                                current_field.remove(record)
                            else:
                                current_field.append(record)

                    else:
                        setattr(instance, field_name, field_value)

                db.session.add(instance)
                db.session.flush()

                if instance_is_new:
                    instance_model_data = pythonfosdem.models.ModelData(name=xml_id,
                                                                        ref_model=xml_record.model,
                                                                        ref_id=instance.id)
                    db.session.add(instance_model_data)
                    db.session.flush()

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
