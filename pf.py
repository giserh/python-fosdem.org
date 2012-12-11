# -*- coding: utf-8 -*-
#!/usr/bin/env python
import multiprocessing
from gunicorn.app.base import Application
from werkzeug.contrib.fixers import ProxyFix

from pythonfosdem import create_app
from pythonfosdem.config import DefaultConfig


def count_worker():
    return (multiprocessing.cpu_count() * 2) + 1


class PythonFosdemApp(Application):
    def __init__(self, options=None):
        if options is None:
            options = {}

        self.usage = None
        self.callable = None
        self.options = options
        self.do_load_config()

    def init(self, parser, opts, args):
        config = dict(
            (key, value)
            for key, value in map(lambda item: (item[0].lower(), item[1]), self.options.iteritems())
            if key in self.cfg.settings and value is not None
        )
        return config

    def load(self):
        application = create_app(DefaultConfig)
        application.wsgi_app = ProxyFix(application.wsgi_app)
        return application

if __name__ == '__main__':
    options = {
        'bind': '127.0.0.1:19000',
        # 'debug': True,
        # 'loglevel': 'debug',
        'pidfile': '/tmp/www.python-fosdem.org.pid',
        'proc_name': 'PythonFOSDEM',
        'workers': count_worker(),
    }

    pf = PythonFosdemApp(options)
    pf.run()
