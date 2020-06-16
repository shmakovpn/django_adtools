Deploying under Linux Centos 7 using Apache
===========================================

 This article contains some notes how to deploy a Django website
 on a server under Centos 7.

 Install and configure packages

  .. code-block:: bash

   sudo yum install -y python3
   sudo yum install -y python3-devel
   sudo  yum install -y openldap-devel
   sudo yum install -y gcc
   pip3 install --user virtualenv
   sudo yum install -y httpd
   sudo sed -i /etc/sysconfig/httpd -re 's/^(LANG=C)/#\1/'
   sudo yum install -y httpd-devel
   sudo pip install mod_wsgi
   sudo yum install -y postgresql-server
   sudo -i -u postgres /bin/postgresql-setup initdb
   sudo -i -u postgres sed -i data/pg_hba.conf -e 's/ident/md5/'
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   DB_NAME=your_db_name
   sudo -i -u postgres psql -c "CREATE DATABASE $DB_NAME ENCODING 'utf8'"
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   sudo -i -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD'"
   sudo -i -u postgres psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER"
   sudo -i -u postgres psql -c "ALTER USER $DB_USER CREATEDB"  # if you need to run tests
   PROJECT_NAME=some_name
   sudo mkdir /var/www/$PROJECT_NAME
   sudo chown apache:apache /var/www/$PROJECT_NAME
   sudo setfacl -R -m u:$(whoami):rwx /var/www/$PROJECT_NAME
   sudo setfacl -R -d -m u:$(whoami):rwx /var/www/$PROJECT_NAME
   virtualenv /var/www/$PROJECT_NAME/venv -p /usr/bin/python3
   source /var/www/$PROJECT_NAME/venv/bin/activate
   cd /var/www/$PROJECT_NAME
   pip install django_adtools
   pip install psycopg2-binary
   django-admin startproject $PROJECT_NAME .

 Edit /var/www/$PROJECT_NAME/$PROJECT_NAME/settings.py

  .. code-block:: python

   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django_adtools',
   ]

  .. code-block:: python

   DATABASES = {
        'default': {
           'ENGINE': 'django.db.backends.postgresql_psycopg2',
           'NAME': DB_NAME,
           'USER': DB_USER',
           'PASSWORD': DB_PASSWORD,
           'HOST': 'localhost',
           'PORT': '',
        }
   }

  .. code-block:: python

   # DJANGO_ADTOOLS
   ADTOOLS_DOMAIN: str = 'example.com'  #: name of a windows domain
   # set list of dns servers if your server work under Windows
   # ADTOOLS_NAMESERVERS: List[str] = ['127.0.0.1']  #: list of dns servers to discover ip addresses of domain controllers
   ADTOOLS_TEST_USERNAME: str = 'test@example.com'  #: test ad username
   ADTOOLS_TEST_PASSWORD: str = 'somepassword'  #: test ad password
   ADTOOLS_TEST_GROUP: str = 'test-users'  #: test ad group

 Create and apply migrations

  .. code-block:: bash

   python manage.py makemigrations django_adtools
   python manage.py migrate

 Run tests if need. Your DB_USER must have CREATEDB privileges

  .. code-block:: bash

   python manage.py test django_adtools

 Configure discovering of a Domain Controller

  .. code-block:: bash

   sudo sed -i /etc/crontab -e "\\$a\*/30 \*  \*  \*  \*  apache /var/www/$PROJECT_NAME/venv/bin/python /var/www/$PROJECT_NAME/manage.py discover"
   sudo systemctl reload crond
   sudo -u apache /var/www/$PROJECT_NAME/venv/bin/python /var/www/$PROJECT_NAME/manage.py discover

 Configure firewalld for httpd

  .. code-block:: bash

    sudo firewall-cmd --zone=public --add-service=http --permanent
    sudo firewall-cmd --reload

 Configure http. Create and edit /etc/httpd/conf.d/$PROJECT_NAME.conf

  .. code-block:: apache

   LoadModule wsgi_module /usr/local/lib64/python3.6/site-packages/mod_wsgi/server/mod_wsgi-py36.cpython-36m-x86_64-linux-gnu.so
   WSGIPythonPath /var/www/$PROJECT_NAME
   WSGIPythonHome /var/www/$PROJECT_NAME/venv
   <VirtualHost *:80>
       ServerName $PROJECT_NAME.example.com
        # django admin aliases
        Alias /static/admin /var/www/$PROJECT_NAME/venv/lib/python3.6/site-packages/django/contrib/admin/static/admin
        <Directory /var/www/$PROJECT_NAME/venv/lib/python3.6/site-packages/django/contrib/admin/static/admin>
            Require all granted
        </Directory>
        WSGIScriptAlias / /var/www/$PROJECT_NAME/$PROJECT_NAME/wsgi.py
        WSGIPassAuthorization On
        <Directory /var/www/$PROJECT_NAME/$PROJECT_NAME>
            <Files wsgi.py>
                Require all granted
            </Files>
        </Directory>
   </VirtualHost>

 Configure SELinux

  Install packages

   .. code-block:: bash

    sudo yum install -y policycoreutils
    sudo yum install -y policycoreutils-python

  By default SELinux will suppress AVC log messages from httpd. For disable this behavior, run:

   .. code-block:: bash

    sudo semodule -DB

  To turn back SELinux to default mode (enable dontaudit rules):

   .. code-block:: bash

    sudo semodule -B

  Apply needed SELinux context to the virtualenv folder

   .. code-block:: bash

    sudo semanage fcontext -a -t httpd_sys_script_exec_t '/var/www/$PROJECT_NAME/venv(/.*)?'
    sudo restorecon -Rv /var/www/$PROJECT_NAME/venv

 Run httpd

   .. code-block:: bash

    sudo chown -R apache:apache /var/www/$PROJECT_NAME
    sudo systemctl enable httpd
    sudo systemctl start httpd



