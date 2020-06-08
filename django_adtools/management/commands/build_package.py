"""
django_adtools/management/commands/build_package.py
This script runs 'python setup.py sdist'
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-08'

import os
from django.core.management.base import BaseCommand
SCRIPT_DIR: str = os.path.dirname(os.path.realpath(__file__))


def run_setup():
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
    os.chdir(base_dir)
    os.system(f'python setup.py sdist')
    print('__END__')


class Command(BaseCommand):
    """
    Runs 'python setup.py sdist'
    """
    help = """Setuptools wrapper. Runs 'python setup.py sdist'."""

    def handle(self, *args, **options):
        run_setup()


if __name__ == '__main__':
    run_setup()
