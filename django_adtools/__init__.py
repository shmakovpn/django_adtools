"""
django_adtools/__init__.py
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-05'

import os
import logging
from django.conf import settings
from . import ad
from . import dns

PROJECT_NAME: str = os.path.basename(settings.BASE_DIR)  #: the name of the django project
#: the global logger using in this package
logger: logging.Logger = logging.getLogger(f'django.{PROJECT_NAME}.{__package__}')

