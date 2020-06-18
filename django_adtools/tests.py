from django.test import TestCase
from django.test import override_settings
from django.conf import settings
from typing import List, Optional
import os
import django_adtools.dns
import django_adtools.ad
from .models import *
from io import StringIO
from django.core.management import call_command


# Create your tests here.
class TestDiscoverDC(TestCase):
    def test_re_ip(self):
        """
        Tests re_ip regex pattern to match ipv4 addresses only
        :return: None
        """
        re_ip = django_adtools.dns.discover_dc.re_ip
        self.assertIsNotNone(re_ip.search('127.0.0.1'))
        self.assertIsNotNone(re_ip.search('10.1.2.3'))
        self.assertIsNone(re_ip.search('256.255.255.0'))

    def test_discover(self):
        domain: str = getattr(settings, 'ADTOOLS_DOMAIN', None)
        self.assertIsNotNone(domain, "'ADTOOLS_DOMAIN' does not present in settings.py")
        name_servers: Optional[List[str]] = getattr(settings, 'ADTOOLS_NAMESERVERS', None)
        if os.name == 'nt':
            self.assertIsNotNone(name_servers, "'ADTOOLS_NAMESERVERS' does not present in settings.py on Windows")
        dcs = django_adtools.dns.discover_dc.DCList(domain=domain, name_servers=name_servers)
        dc_list = dcs.get_dc_list()
        self.assertIsNotNone(dc_list, 'Could not get a list of Domain Controllers')
        dc: str = dcs.get_available_dc_ip()
        self.assertIsNotNone(dc, "Could not get an available Domain Controller")


class TestSettings(TestCase):
    """
    This class contains tests for the settings.py file
    """
    def test_installed_apps(self):
        """
        Checks that 'django_adtools' are in INSTALLED_APPS
        :return: None
        """
        self.assertIn(__package__, settings.INSTALLED_APPS)


class TestDomainControllerModel(TestCase):
    def test_domain_controller_model(self):
        ip: str = '127.0.0.1'
        DomainController.set(ip=ip)
        dc: str = DomainController.get()
        self.assertIsNotNone(dc)


class TestManagementCommands(TestCase):
    def test_discovery(self) -> None:
        """
        Tests 'python manage.py discover' command
        :return:
        """
        out = StringIO()
        result = call_command('discover', stdout=out)
        self.assertIsNone(result)
        self.assertEqual(out.getvalue(), '')
        dc: str = DomainController.get()
        self.assertIsNotNone(dc)

    # todo change settings for django logger, for StreamWritter logger, from stderr to custom StringIO()
    @override_settings(DEBUG=True)
    def test_logger(self) -> None:
        err = StringIO()
        out = StringIO()
        result = call_command('logger', 'error', 'hello world', stderr=err, stdout=out)
        print(f'settings.DEBUG={settings.DEBUG}')
        print(f'result={result}')
        print(f'stderr={err.getvalue()}')
        print(f'stdout={out.getvalue()}')


class TestADTools(TestCase):
    def test_clear_username(self):
        self.assertEqual(django_adtools.ad.ad_tools.ad_clear_username('user@domain.com'), 'user')
        self.assertEqual(django_adtools.ad.ad_tools.ad_clear_username('DOMAIN\\user'), 'user')

    def test_login(self):
        if settings.ADTOOLS_TEST_USERNAME and settings.ADTOOLS_TEST_PASSWORD:
            name_servers: Optional[List[str]] = getattr(settings, 'ADTOOLS_NAMESERVERS', None)
            if os.name == 'nt':
                self.assertIsNotNone(name_servers, "'ADTOOLS_NAMESERVERS' does not present in settings.py on Windows")
            dc: str = django_adtools.dns.discover_dc.DCList(
                domain=settings.ADTOOLS_DOMAIN,
                name_servers=name_servers
            ).get_available_dc_ip()
            self.assertIsNotNone(dc, 'Could not discover a Domain Controller')
            conn = django_adtools.ad.ad_tools.ldap_conn(
                dc=dc,
                username=settings.ADTOOLS_TEST_USERNAME,
                password=settings.ADTOOLS_TEST_PASSWORD
            )
            self.assertIsNotNone(conn, 'Could not connect to Domain Controller')
            dn: str = django_adtools.ad.ad_tools.user_dn(
                conn=conn,
                username=settings.ADTOOLS_TEST_USERNAME,
                domain=settings.ADTOOLS_DOMAIN
            )
            self.assertIsNotNone(
                dn,
                f'Could not get a Distinguished Name of user: {settings.ADTOOLS_TEST_USERNAME}'
            )
            print(f"Distinguished Name of user: {settings.ADTOOLS_TEST_USERNAME} is {dn}")
            groups: List[str] = django_adtools.ad.ad_tools.dn_groups(
                conn=conn,
                dn=dn,
                domain=settings.ADTOOLS_DOMAIN
            )
            self.assertIsNotNone(groups, f"Could not get groups for user {dn}")
            self.assertGreater(len(groups), 0, f'An empty groups array got for user {dn}')
            print(f"ad_groups: {groups}")
            self.assertIn(settings.ADTOOLS_TEST_GROUP, groups)



