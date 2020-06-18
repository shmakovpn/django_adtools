"""
django_adtools/management/commands/devel_info.py
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-18'

import os
from django.core.management import BaseCommand
from django_adtools import logger
from django.conf import settings

PROJECT_NAME: str = os.path.basename(settings.BASE_DIR)  #: the name of the django project


class Command(BaseCommand):
    """
    Prints some information about django_adtools package
    """
    help = 'Prints some information about django_adtools package'

    def handle(self, *args, **options):
        print(f"base_dir={settings.BASE_DIR}")
        print(f"project_name={PROJECT_NAME}")
        print(f"__name__={__name__}")
        print(f"package={logger}")
        logger.debug('logger debug message')
        logger.info('logger info message')
        logger.warning('logger warning message')
        logger.error('logger error message')
        logger.critical('logger critical message')

