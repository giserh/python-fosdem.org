#!/usr/bin/env bash
#psql -d python_fosdem_org -c "DROP TABLE talk;"
#./manage.py db_create -c $PWD/conf/production.cfg
#./manage.py import_xml pythonfosdem/data/pythonfosdem_init.xml -c $PWD/conf/production.cfg
#./manage.py import_xml pythonfosdem/data/pythonfosdem_user.xml -c $PWD/conf/production.cfg
#./manage.py cleanup_database -c $PWD/conf/production.cfg

./manage.py import_xml pythonfosdem/data/pythonfosdem_init.xml -c $PWD/conf/production.cfg
./manage.py import_xml pythonfosdem/data/pythonfosdem_user.xml -c $PWD/conf/production.cfg
