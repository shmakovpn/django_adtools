Usage Examples
==============

 Start a new django application *ad_example*

  .. code-block:: bash

   python manage.py startapp ad_example

 Edit /var/www/$PROJECT_NAME/$PROJECT_NAME/settings.py. Add *ad_example* to *INSTALLED_APPS*

  .. code-block:: python

   INSTALLED_APPS = [
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',
       'django_adtools',
       'ad_example',
   ]

 Edit /var/www/$PROJECT_NAME/$PROJECT_NAME/settings.py. Add *ADTOOLS* setting

 .. include:: chunks/settings_adtools.rst

 Create and apply migrations

  .. code-block:: bash

   python manage.py makemigrations django_adtools
   python manage.py migrate

 Configure discovering of a Domain Controller. For more information look at :doc:`centos7`

  .. code-block:: bash

   sudo sed -i /etc/crontab -e "\\$a\*/30 \*  \*  \*  \*  apache /var/www/$PROJECT_NAME/venv/bin/python /var/www/$PROJECT_NAME/manage.py discover"
   sudo systemctl reload crond
   sudo -u apache /var/www/$PROJECT_NAME/venv/bin/python /var/www/$PROJECT_NAME/manage.py discover

 Create folder /var/www/$PROJECT_NAME/ad_example/templates/ad_example

  .. code-block:: bash

   mkdir /var/www/$PROJECT_NAME/ad_example/templates/ad_example

 Create base.html template

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/templates/ad_example/base.html

 Edit base.html

  .. code-block:: html

   <!DOCTYPE html>
   <html lang="en">
   <head>
       <meta charset="UTF-8">
       <title>{% block title %}{% endblock %}</title>
   </head>
   <body>
       {% block content %}
       {% endblock %}
   </body>
   </html>

 Create index.html template

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/templates/ad_example/index.html

 Edit index.html template

  .. code-block:: html

   {% extends package|add:'/base.html' %}
   {% block title %}Hello - {{ user }}{% endblock %}
   {% block content %}
       <h1>Hello - {{ user }}</h1>
       <a href="{% url package|add:':logout' %}">Logout</a>
   {% endblock %}

 Create login.html template

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/templates/ad_example/login.html

 Edit login.html template

  .. code-block:: html

   {% extends package|add:'/base.html' %}
   {% block title %}Login{% endblock %}
   {% block content %}
       <h1>Login</h1>
       {% if login_failed %}
           <div>Login failed!!!</div>
       {% endif %}
       <form method="post">
           {% csrf_token %}
           {{ form.as_p }}
           <input type="submit" value="Submit">
       </form>
   {% endblock %}

 Create forms.py file

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/forms.py

 Edit forms.py

  .. code-block:: python

   from django import forms


   class LoginForm(forms.Form):
       username = forms.CharField()
       password = forms.CharField(widget=forms.PasswordInput)

 Edit views.py

  .. code-block:: python

   from django.shortcuts import render, redirect
   from django.views import View
   from django.urls import reverse, reverse_lazy
   from django.contrib.auth.mixins import LoginRequiredMixin
   from .forms import LoginForm
   from django_adtools.models import DomainController
   from django_adtools.ad.ad_tools import ad_login, ad_clear_username
   from django.conf import settings
   from django.contrib.auth.models import User
   from django.contrib.auth import login, logout


   class Index(LoginRequiredMixin, View):
       login_url = reverse_lazy(f'{__package__}:login')
       redirect_field_name = None

       def get(self, request):
           context = {'package': __package__}
           return render(request, f"{__package__}/index.html", context)


   class Login(View):
       def get(self, request):
           form = LoginForm()
           context = {'package': __package__, 'form': form}
           return render(request, f"{__package__}/login.html", context)

       def post(self, request):
           form = LoginForm(request.POST)
           if form.is_valid():
               if ad_login(
                   dc=DomainController.get(),
                   username=form.cleaned_data['username'],
                   password=form.cleaned_data['password'],
                   domain=settings.ADTOOLS_DOMAIN,
                   group=settings.ADTOOLS_GROUP,
               ):
                   # get full domain username like user@domain.ru
                   username_without_domain = ad_clear_username(form.cleaned_data['username'])
                   username = f"{username_without_domain}@{settings.ADTOOLS_DOMAIN}"
                   try:
                       # looking for existing user profile (case insensitive)
                       user = User.objects.get(username__iexact=username)
                   except User.DoesNotExist:
                       # create an user profile if it does not exist
                       user = User(username=username)
                       user.save()
                   login(request=request, user=user)
                   return redirect(reverse(f'{__package__}:index'))
           context = {'package': __package__, 'form': form, 'login_failed': True, }
           return render(request, f"{__package__}/login.html", context)


   class Logout(View):
       def get(self, request):
           logout(request)
           return redirect(reverse(f'{__package__}:login'))

 Create urls.py file

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/urls.py

 Edit /var/www/$PROJECT_NAME/ad_example/urls.py

  .. code-block:: python

   from .views import *
   from django.urls import path

   app_name = __package__
   urlpatterns = [
       path('', Index.as_view(), name='index'),
       path('login/', Login.as_view(), name='login'),
       path('logout/', Logout.as_view(), name='logout'),
   ]

 Edit /var/www/$PROJECT_NAME/$PROJECT_NAME/urls.py

  .. code-block:: python

   from django.contrib import admin
   from django.urls import path
   from django.urls import include  # add this

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('', include('ad_example.urls')),  # add this
   ]

 Run your project

  .. code-block:: bash

   python manage.py runserver

 Open http://localhost:8000 in your browser, then try to login using an Active Directory username and password.

 Also, you can create tests.

  .. code-block:: bash

   touch /var/www/$PROJECT_NAME/ad_example/tests.py

 Edit tests.py

  .. code-block:: python

   from django.test import TestCase
   from django.test.client import Client
   from django.shortcuts import reverse
   from bs4 import BeautifulSoup
   from django.conf import settings
   from django_adtools.dns.discover_dc import DCList
   from django_adtools.models import DomainController


   # Create your tests here.
   class TestExample(TestCase):
       def test_ad_example(self):
           # reading 'username' and 'password' for the test user from config
           username = getattr(settings, 'ADTOOLS_TEST_USERNAME', None)
           self.assertIsNotNone(username)
           password = getattr(settings, 'ADTOOLS_TEST_PASSWORD', None)
           self.assertIsNotNone(password)
           # set an ip address of a Domain Controller
           dc = DCList(
               domain=settings.ADTOOLS_DOMAIN,
               name_servers=getattr(settings, 'ADTOOLS_NAMESERVERS', None),
           ).get_available_dc_ip()
           self.assertIsNotNone(dc)
           self.assertIsNot(dc, '')
           DomainController.set(dc)
           # get login page address
           client = Client(enforce_csrf_checks=True)  # creating the client with csrf_checks are enabled
           response = client.get(reverse(f'{__package__}:index'))
           self.assertIsNotNone(response)
           self.assertEqual(response.status_code, 302)
           login_url = response.url
           # get csrf token
           response = client.get(login_url)
           self.assertIsNotNone(response)
           self.assertEqual(response.status_code, 200)
           soup = BeautifulSoup(response.content.decode(), 'html.parser')
           csrf_element = soup.select_one("form[method='post'] input[name='csrfmiddlewaretoken']")
           self.assertIsNotNone(csrf_element)
           csrf_value = csrf_element.attrs['value']
           # try to login
           response = client.post(reverse(f'{__package__}:login'), data={
               'csrfmiddlewaretoken': csrf_value,
               'username': username,
               'password': password,
           })
           # check that the response is a redirect (302) to the index page (login success)
           self.assertIsNotNone(response)
           self.assertEqual(response.status_code, 302)
           self.assertEqual(response.url, reverse(f"{__package__}:index"))




