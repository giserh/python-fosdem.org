#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    fabfile
    ~~~~~~~

    Tool for the management of Python-FOSDEM.org

    :copyright: (c) 2012-2013 by Stephane Wirtel.
    :license: BSD, see LICENSE for more details.
"""
import os
import datetime
from fabric.api import run
from fabric.api import task
from fabric.api import env
from fabric.api import cd
from fabtools import files
from fabtools import python
from fabtools import require
from fabtools import postgres


def now():
    return datetime.datetime.now()


def working_directory(directory):
    if isinstance(directory, basestring):
        directory = [directory]

    return os.path.join('/', 'home', 'www', *directory)

CACHE_DIRECTORY = '/home/www/pip-cache'
HOME_DIRECTORY = working_directory('python-fosdem.org')

DATABASE = 'python_fosdem_org'
DATABASE_OWNER = 'pythonfosdem'
DATABASE_OWNER_PASSWORD = 'pythonfosdem'

GIT_REPOSITORY = 'git://github.com/matrixise/python-fosdem.org'
SRC_DIR = os.path.join(HOME_DIRECTORY, 'src')
VIRTUALENV_PATH = os.path.join(HOME_DIRECTORY, 'env')
REQUIREMENT_FILE = os.path.join(SRC_DIR, 'pip-requirements.txt')

env.user = 'root'
env.hosts = ['wirtel.be']


@task
def bootstrap():
    require.deb.package('postgresql-server-dev-8.4')
    require.deb.package('libevent-dev')

    postgresql_user_create()
    database_create()

    working_directory_create()
    source_fetch()
    virtualenv_init()


@task
def postgresql_user_create():
    if not postgres.user_exists(DATABASE_OWNER):
        postgres.create_user(DATABASE_OWNER, DATABASE_OWNER_PASSWORD)


@task
def database_create(database=DATABASE):
    require.postgres.database(database, DATABASE_OWNER)


@task
def working_directory_create(directory=HOME_DIRECTORY):
    run('mkdir -p %s/{conf,dump}' % (directory,))
    run('chown -R root:root %s' % (directory,))


@task
def switch_to_maintenance():
    run('')


@task
def switch_to_production():
    run('')


@task
def source_fetch():
    if not files.is_dir(SRC_DIR):
        with cd(HOME_DIRECTORY):
            run('git clone %s src' % (GIT_REPOSITORY,))
    else:
        with cd(SRC_DIR):
            run('git pull')


@task
def virtualenv_init():
    require.python.virtualenv(VIRTUALENV_PATH)
    with python.virtualenv(VIRTUALENV_PATH):
        require.python.requirements(REQUIREMENT_FILE,
                                    download_cache=CACHE_DIRECTORY)


@task
def database_backup():
    filename = '%s_%s.dump.sql' % (DATABASE, now().strftime('%Y%m%d_%H%M'))
    dump_file = os.path.join(HOME_DIRECTORY, 'dump', filename)
    run('pg_dump --no-owner %s > %s' % (DATABASE, dump_file))


@task
def working_directory_drop():
    run('rm -rf %s' % (HOME_DIRECTORY))


@task
def postgresql_user_drop():
    postgres._run_as_pg("""psql -c 'drop user %s'""" % (DATABASE_OWNER))


@task
def database_drop():
    postgres._run_as_pg("""psql -c 'drop database %s'""" % (DATABASE,))
