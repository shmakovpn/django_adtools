"""
django_adtools/management/commands/logger.py
"""
from django.core.management import BaseCommand
import django.core.management.base
import logging
from django_adtools import logger


class Command(BaseCommand):
    """
    Writes message to log using the logger defined in this package

    >>> python manage.py logger info hello world
    hello world
    """
    help = "Writes message to log using the logger defined in this package"

    def add_arguments(self, parser: django.core.management.base.CommandParser) -> None:
        parser.add_argument('log_level', nargs=1, type=str, help='debug, info, warning, error or critical', choices=[
            'debug', 'info', 'warning', 'error', 'critical',
        ])
        parser.add_argument('message', nargs='+', type=str, help='log message')

    def handle(self, *args, **options) -> None:
        log_level: str = options['log_level'][0]
        message: str = ' '.join(options['message'])
        logger.log(getattr(logging, log_level.upper()), '%s', message)
        print(f'log_level={log_level}, message={message}')
        self.stdout.write('some hello from stdout')
        self.stderr.write('some error')
