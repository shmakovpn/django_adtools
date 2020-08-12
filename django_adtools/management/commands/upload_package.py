"""
django_adtools/management/commands/upload_package.py
This script runs 'twine upload dist/django-adtools-{VERSION}.tar.gz'
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-08'

import os
from django.core.management.base import BaseCommand
from django_adtools.version import VERSION
SCRIPT_DIR: str = os.path.dirname(os.path.realpath(__file__))


def run_upload():
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
    dist_dir: str = os.path.join(base_dir, 'dist')
    dist_file: str = os.path.join(dist_dir, f'django-adtools-{VERSION}.tar.gz')
    os.system(f'twine upload --verbose {dist_file}')
    print('__END__')


class Command(BaseCommand):
    """
    Runs 'twine upload dist/django-adtools-{VERSION}.tar.gz'
    """
    help = """Twine wrapper. Runs 'twine upload dist/django-adtools-{VERSION}.tar.gz'."""

    def handle(self, *args, **options):
        run_upload()


if __name__ == '__main__':
    run_upload()
