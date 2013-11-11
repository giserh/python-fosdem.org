# -*- coding: utf-8 -*-
import os
import re
from jinja2 import Markup
import sqlalchemy
import pythonfosdem.models
import pythonfosdem.xml_importer
from pythonfosdem.extensions import db

HERE = os.path.dirname(__file__)
DATA_DIR = os.path.abspath(os.path.join(HERE, 'data'))


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Took from pelican source (which took it from django sources).
    """
    value = Markup(value).striptags()
    if type(value) == unicode:
        import unicodedata
        from unidecode import unidecode
        value = unicode(unidecode(value))
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)

def is_relationship(model, field):
    return isinstance(model.__mapper__._props[field],
                      sqlalchemy.orm.properties.RelationshipProperty)


def field_from_to(meta, field):
    field_from = field_to = False
    field_type = meta.__mapper__._props[field]
    meta_table = meta.__table__.name

    for column in field_type.secondary.columns:
        for fk in column.foreign_keys:
            if fk.column.table.name == meta_table:
                field_from = (column.name, fk.column.table.name, fk.column.name)
            else:
                field_to = (column.name, fk.column.table.name, fk.column.name)

    return field, field_from, field_to


def get_xml_id_or_raise(xml_id):
    model_data = pythonfosdem.models.ModelData.query.filter_by(name=xml_id).first()
    if model_data is not None:
        proxy = getattr(pythonfosdem.models, model_data.ref_model)
        return model_data.ref_model, model_data.ref_id, proxy.query.get(model_data.ref_id)

    raise Exception("The requested XML ID (%s) does not exists" % (xml_id,))


def create_or_update(model_class, xml_id):
    model_data = pythonfosdem.models.ModelData.query.filter_by(name=xml_id).first()
    proxy = getattr(pythonfosdem.models, model_class)
    if not model_data:
        return proxy(), proxy
    else:
        return proxy.query.get(model_data.ref_id), proxy


def import_xml(filename):
    if not os.path.exists(filename):
        print "The %s file does not exists" % (filename,)
        return

    with open(filename, 'r') as fp:
        xml_records = pythonfosdem.xml_importer.parse(fp)

        for xml_id, xml_record in xml_records.iteritems():
            instance, proxy = create_or_update(xml_record.model, xml_id)
            instance_is_new = instance.id is None

            for field_name, field_value in xml_record.fields.iteritems():
                current_field = getattr(instance, field_name)

                if isinstance(field_value, dict) and 'reference' in field_value:
                    ref_model, ref_id, record = get_xml_id_or_raise(field_value['reference'])
                    setattr(instance, field_name, record)
                elif is_relationship(proxy, field_name):
                    for nested_xml_id in xml_record.fields[field_name].split(','):
                        operator = '+'
                        if nested_xml_id[0] in ('+', '-'):
                            operator, nested_xml_id = nested_xml_id[0], nested_xml_id[1:]

                        ref_model, ref_id, record = get_xml_id_or_raise(nested_xml_id)

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


def reset_db():
    db.drop_all()
    db.create_all()
    import_xml(os.path.join(DATA_DIR, 'pythonfosdem_init.xml'))
    import_xml(os.path.join(DATA_DIR, 'pythonfosdem_user.xml'))
    import_xml(os.path.join(DATA_DIR, 'pythonfosdem_demo.xml'))
