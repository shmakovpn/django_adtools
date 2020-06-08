"""
django_adtools/management/commands/makedoc.py
This script runs 'sphinx-build -b html docs/source docs/build/html'
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-08'

import os
from django.core.management.base import BaseCommand
SCRIPT_DIR: str = os.path.dirname(os.path.realpath(__file__))


def run_sphinx():
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
    docs_dir: str = os.path.join(base_dir, 'docs')
    docs_source_dir: str = os.path.join(docs_dir, 'source')
    build_dir: str = os.path.join(docs_dir, 'build')
    html_dir: str = os.path.join(build_dir, 'html')
    os.system(f'sphinx-build -b html {docs_source_dir} {html_dir}')
    print('__END__')


class Command(BaseCommand):
    """
    Runs 'sphinx-build -b html docs/source docs/build/html'
    """
    help = """Sphinx-build wrapper. Runs 'sphinx-build -b html docs/source docs/build/html'."""

    def handle(self, *args, **kwargs):
        run_sphinx()


if __name__ == '__main__':
    run_sphinx()
