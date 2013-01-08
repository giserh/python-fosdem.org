#!/usr/bin/env bash
#psql -d python_fosdem_org -c "DROP TABLE talk;"
#./manage.py db_create -c $PWD/conf/production.cfg
#./manage.py import_xml pythonfosdem/data/pythonfosdem_init.xml -c $PWD/conf/production.cfg
#./manage.py import_xml pythonfosdem/data/pythonfosdem_user.xml -c $PWD/conf/production.cfg
#./manage.py cleanup_database -c $PWD/conf/production.cfg

# psql -d python_fosdem_org -c 'ALTER TABLE "user" ADD COLUMN photo_path VARCHAR(255);'
# ./manage.py import_xml pythonfosdem/data/pythonfosdem_init.xml -c $PWD/conf/production.cfg
# ./manage.py import_xml pythonfosdem/data/pythonfosdem_user.xml -c $PWD/conf/production.cfg

# psql -d python_fosdem_org <<EOF
# ALTER TABLE talk ADD COLUMN tmp_created_at TIMESTAMP;
# UPDATE talk SET tmp_created_at = created_at;
# ALTER TABLE talk DROP COLUMN created_at;
# ALTER TABLE talk RENAME COLUMN tmp_created_at TO created_at;
# ALTER TABLE talk ADD COLUMN start_at TIMESTAMP;
# ALTER TABLE talk ADD COLUMN stop_at TIMESTAMP;
# ALTER TABLE talk ADD COLUMN type VARCHAR(16) DEFAULT 'talk';
# EOF

# ALTER TABLE talk ADD COLUMN start_at TIMESTAMP WITH TIME ZONE;
# ALTER TABLE talk ADD COLUMN stop_at TIMESTAMP WITH TIME ZONE;

psql -d python_fosdem_org <<EOF
ALTER TABLE model_data ADD COLUMN tmp_created_at TIMESTAMP;
UPDATE model_data SET tmp_created_at = created_at;
ALTER TABLE model_data DROP COLUMN created_at;
ALTER TABLE model_data RENAME COLUMN tmp_created_at TO created_at;

ALTER TABLE role ADD COLUMN tmp_created_at TIMESTAMP;
UPDATE role SET tmp_created_at = created_at;
ALTER TABLE role DROP COLUMN created_at;
ALTER TABLE role RENAME COLUMN tmp_created_at TO created_at;

ALTER TABLE "user" ADD COLUMN tmp_created_at TIMESTAMP;
UPDATE "user" SET tmp_created_at = created_at;
ALTER TABLE "user" DROP COLUMN created_at;
ALTER TABLE "user" RENAME COLUMN tmp_created_at TO created_at;

EOF
