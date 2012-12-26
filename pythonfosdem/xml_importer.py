#!/usr/bin/env python
from lxml import etree


class Record(object):
    def __init__(self, model, xml_id=None):
        self.model = model
        self.xml_id = xml_id
        self.fields = {}

    def field(self, name, value):
        self.fields[name] = value

    def to_struct(self):
        return {
            '_instance_': (self.model, None, self.xml_id),
            'fields': self.fields.items()
        }


def parse(records, file_like):
    content = file_like.read()

    tree = etree.fromstring(content)

    for item_record in tree.findall('record'):
        model = item_record.get('model')
        xml_id = item_record.get('id')
        records[xml_id] = Record(model, xml_id)

        for field in item_record.findall('field'):
            records[xml_id].fields[field.get('name')] = field.text
