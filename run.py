#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    run.py
    ~~~~~~

    :copyright: (c) 2012 Stephane Wirtel <stephane@wirtel.be>
"""
import os
DOCUMENT_ROOT = os.path.dirname(__file__)
if 'VIRTUAL_ENV' in os.environ:
    ENVIRONMENT = os.environ['VIRTUAL_ENV']
else:
    ENVIRONMENT = os.path.join(DOCUMENT_ROOT, 'environment')
EGG_DIRECTORY = os.path.join(DOCUMENT_ROOT, 'eggs')

activate_this = os.path.join(ENVIRONMENT, 'bin', 'activate_this.py')
execfile(activate_this, dict(__file__=activate_this))

os.environ['PYTHON_EGG_CACHE'] = EGG_DIRECTORY

import multiprocessing
from gunicorn.app.base import Application
from werkzeug.contrib.fixers import ProxyFix

from pf import PythonFosdemApp, count_worker

if __name__ == '__main__':
    options = {
        'bind': '127.0.0.1:19000',
        'debug': True,
        'loglevel': 'debug',
        'pidfile': '/tmp/www.python-fosdem.org.pid',
        'proc_name': 'PythonFOSDEM',
        'workers': count_worker(),
    }

    pf = PythonFosdemApp(options)
    pf.run()

