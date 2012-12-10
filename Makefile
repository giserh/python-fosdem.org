.PHONY: clean-pyc test
all: clean-pyc 

clean-pyc:
	find . -name "*.pyc" -or -name "*.pyo" -or -name "*~" | xargs rm -f

i18n-extract:
	pybabel extract -F pythonfosdem/config/babel.cfg -k lazy_gettext -o pythonfosdem/translations/pythonfosdem.pot .

i18n-init: i18n-extract
	pybabel init -i pythonfosdem/translations/pythonfosdem.pot -d pythonfosdem/translations -l fr_FR
	pybabel init -i pythonfosdem/translations/pythonfosdem.pot -d pythonfosdem/translations -l en_US
	pybabel init -i pythonfosdem/translations/pythonfosdem.pot -d pythonfosdem/translations -l nl_NL


i18n-update: i18n-extract
	pybabel update -i pythonfosdem/translations/pythonfosdem.pot -d pythonfosdem/translations

i18n-compile: 
	pybabel compile -d pythonfosdem/translations

recreate_db:
	python manage.py db_drop
	python manage.py db_create
	python manage.py db_populate

