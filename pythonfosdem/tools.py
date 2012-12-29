# -*- coding: utf-8 -*-
import re
from jinja2 import Markup
import sqlalchemy
import pythonfosdem.models

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
