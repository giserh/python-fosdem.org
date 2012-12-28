#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
manage.py
~~~~~~~~~

The command line of Python-FOSDEM.org

:copyright: (c) 2012 by Stephane Wirtel.
:license: BSD, see LICENSE for more details.

Usage:
    manage.py -h | --help
    manage.py [options] run [-p PORT | --port=PORT]
    manage.py [options] drop
    manage.py [options] create [-d|--drop]
    manage.py [options] import <FILE>...

Options:
    -c CONFIG_FILE          Config file to load
    -p PORT --port=PORT     Specify on with port the server must run [default: 5000]
    -d --drop               Drop database before recreating

"""
import os
import sys
import docopt
from pythonfosdem import create_app
from pythonfosdem.extensions import db
import pythonfosdem.tools
import pythonfosdem.models
import pythonfosdem.xml_importer


def main():
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

    app = create_app()

    opts = docopt.docopt(__doc__)
    if opts.get('-c'):
        c = os.path.realpath(opts['-c'])
        try:
            app.config.from_pyfile(c)
        except IOError, e:
            sys.exit(e)

    with app.test_request_context():
        if opts.get('drop') or opts.get('--drop'):
            db.drop_all()
        if opts.get('create'):
            db.create_all()

        if opts.get('import'):
            for f in opts['<FILE>']:
                import_xml(f)

        if opts.get('run'):
            app.run(port=int(opts['--port']))


if __name__ == '__main__':
    main()
