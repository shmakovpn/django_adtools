"""
setup.py
django-adtools installation script
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-08'


import os
from setuptools import setup, find_packages
from django_adtools.version import VERSION

# allow setup.py to be run from any path
SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)

with open('README.rst') as f:
    long_description: str = f.read()

setup(
    name='django-adtools',
    version=VERSION,
    packages=find_packages(),
    author='shmakovpn',
    author_email='shmakovpn@yandex.ru',
    url='https://github.com/shmakovpn/django_adtools',
    download_url=f'https://github.com/shmakovpn/django_ocr_server/archive/{VERSION}.zip',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    entry_points={
        'console_sripts': [],
    },
    install_requires=[
        'Django',
        'dnspython',
        'python-ldap',
        'dnslib',  # using in tests like DNS Server emulator
        'unittest-dataprovider',  # using in tests like PHP @dataprovider
        # 'python-ldap-test',  # using in test like LDAP Server emulator
    ],
    include_package_data=True,
    # test_suite='tests',
)
