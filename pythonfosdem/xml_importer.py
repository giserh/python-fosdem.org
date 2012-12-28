#!/usr/bin/env python
try:
    from collections import OrderedDict
except ImportError:
    import sys
    if sys.python_version[:2] < (2, 7):
        from ordereddict import OrderedDict     # noqa
    else:
        raise

from lxml import etree


class Record(object):
    def __init__(self, model, xml_id=None):
        self.model = model
        self.xml_id = xml_id
        self.fields = {}

    def field(self, name, value):
        self.fields[name] = value


def parse(file_like):
    records = OrderedDict()
    content = file_like.read()

    tree = etree.fromstring(content)

    for item_record in tree.findall('record'):
        model = item_record.get('model')
        xml_id = item_record.get('id')
        records[xml_id] = Record(model, xml_id)

        for field in item_record.findall('field'):
            if field.get('reference'):
                records[xml_id].fields[field.get('name')] = {'reference': field.get('reference')}
            else:
                records[xml_id].fields[field.get('name')] = field.text

    return records
