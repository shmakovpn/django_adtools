Installation
============

Windows 10
----------

 Install Django https://docs.djangoproject.com/en/3.0/howto/windows/

 Install packages

  | *cd your/project/folder*
  | download binaries to install python-ldap on Windows from
    https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap
    You have to choose a *whl* package for your system.
    For example *win_amd64*.
    Then run:
  | *pip install download/path/python_ldap-3.2.0-cp37-cp37m-win_amd64.whl*
  | *pip install django-adtools*

Linux
-----
 Install linux packages

  | *sudo yum -y install gcc*
  | *sudo yum -y install python36-devel* # if your python version is 3.6
  | *sudo yum -y install openldap-devel*

 Install python packages

  | *pip install django-adtools*

