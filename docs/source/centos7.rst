Linux, Centos 7
===============

 This article contains some notes how to deploy a Django website
 on a server under Centos 7.

 Install and configure packages

  | *sudo yum install -y python3*
  | *pip3 install --user virtualenv*
  | *sudo yum install -y httpd*
  | *sudo yum install -y mod_wsgi*
  | *sudo yum install -y postgresql-server*
  | *sudo -i -u postgres /bin/postgresql-setup initdb*
  | *sudo -i -u postgres sed -i data/pg_hba.conf -e 's/ident/md5/'*
  | *sudo systemctl enable postgresql*
  | *sudo systemctl start postgresql*
  | *DB_NAME=your_db_name*
  | *sudo -i -u postgres psql -c "CREATE DATABASE $DB_NAME ENCODING 'utf8'"*
  | *DB_USER=your_db_user*
  | *DB_PASSWORD=your_db_password*
  | *sudo -i -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'"*
  | *sudo -i -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER"*
  | *PROJECT_NAME=some_name*
  | *sudo mkdir /var/www/$PROJECT_NAME*
  | *sudo chown apache:apache /var/www/$PROJECT_NAME*
  | *sudo setfacl -R -m u:$(whoami):rwx /var/www/$PROJECT_NAME*
  | *sudo setfacl -R -d -m u:$(whoami):rwx /var/www/$PROJECT_NAME*
  | *virtualenv /var/www/$PROJECT_NAME/venv -p /usr/bin/python3*
  | *source /var/www/$PROJECT_NAME/venv/bin/activate*
  | cd /var/www/$PROJECT_NAME
  | django-admin startproject $PROJECT_NAME .
todo!!! | pip install django_adtools



 !!!todo | pip install mod_wsgi
