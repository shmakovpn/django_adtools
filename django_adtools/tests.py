from django.conf import settings
from typing import List, Tuple, ContextManager, Optional, TextIO
# import os

# testing libraries
from django.test import TestCase, override_settings
from unittest_dataprovider import data_provider

# django_adtools
# import django_adtools.ad
from django_adtools.ad.ad_tools import ad_clear_username, ldap_connect
from django_adtools.dns.discover_dc import DCList, re_ip

# emulation of a DNS Server
from dnslib.zoneresolver import ZoneResolver
from dnslib.server import DNSServer

# emulaiton of a LDAP Server
# import slapdtest # requires ldapadd (apt install ldap-utils)
#    and does not work without it, requires slapd (apt install slapd)
# from ldaptools import slapd
# from ldap_test import LdapServer

# import logging
# from django_adtools import logger
from .models import *
# from io import StringIO
# from django.core.management import call_command


# the simple DNS zone file for testing getting SRV records from dnslib.DNSServer (the python emulator of DNS Server)
zone_file: str = """
{domain}.               600   IN   SOA   localhost localhost ( 2007120710 1d 2h 4w 1h )
{domain}.               400   IN   NS    localhost
{domain}.               600   IN   A     127.0.0.1
controller.{domain}.          IN   A     127.0.0.1
_ldap._tcp.dc._msdcs.{domain}.    600   IN   SRV   1 10 {port} {srv_address}."""

domain: str = 'domain.local'  # testing name of the domain


class TestDiscoverDC(TestCase):
    @staticmethod
    def ip_addresses() -> Tuple[
        Tuple[str, bool], Tuple[str, bool], Tuple[str, bool], Tuple[str, bool], Tuple[str, bool]
    ]:
        """
        Dataprovider for test_re_ip
        """
        return (
            ('127.0.0.1', True,),
            ('10.1.2.3', True,),
            ('256.255.255.0', False,),
            ('something', False,),
            ('0.0.0.0', True,),
        )

    @data_provider(ip_addresses)
    def test_re_ip(self, ip_address: str, is_valid_ip: bool):
        """
        Tests re_ip regex pattern to match ipv4 addresses only
        """
        self.assertEqual(bool(re_ip.search(ip_address)), is_valid_ip)

    @staticmethod
    def srv_addresses() -> Tuple[Tuple[str], Tuple[str], ]:
        """
        Dataprovider for test_discover
        """
        return (
            (f'controller.{domain}',),
            ('127.0.0.1',),
        )

    @data_provider(srv_addresses)
    def test_discover(self, srv_address: str):

        # setups the LDAP Server emulator, slapdtest.SlapdObject requires ldapadd and does not work without it
        # with slapdtest.SlapdObject() as ldap_server:
        #      print(ldap_server)

        # ldap_server = LdapServer()  # зависает
        # slapd_server = slapd.Slapd()

        name_servers: List[str] = ['127.0.0.1']  # the list of nameservers
        # configures the DNS Server
        zone_resolver: ZoneResolver = ZoneResolver(
            zone=zone_file.format(domain=domain, srv_address=srv_address, port=389),
        )
        # port=0 means that the DNS Server will choose a free UDP Port
        dns_server: DNSServer = DNSServer(resolver=zone_resolver, port=0, tcp=False)
        dns_server.start_thread()  # start the DNS Server in a separate python thread
        port: int = dns_server.server.server_address[1]  # gets the number of the UDP Port
        # discover for domain controllers
        dc_list: DCList = DCList(domain=domain, nameservers=name_servers, port=port)
        self.assertIsNotNone(dc_list.get_dc_list(), 'Could not get a list of Domain Controllers')
        # try to get an available domain controller
        # todo DCHostname.ping need to emulate ldap server!!!
        dc: str = dc_list.get_available_dc_ip()
        print(f"dc={dc}")
        self.assertIsNotNone(dc, "Could not get an available Domain Controller")
        # stop DNS Server
        dns_server.server.server_close()
        dns_server.stop()


class TestSettings(TestCase):
    """
    This class contains tests for the settings.py file
    """

    def test_installed_apps(self):
        """
        Checks that 'django_adtools' are in INSTALLED_APPS
        """
        self.assertIn(__package__, settings.INSTALLED_APPS)


class TestDomainControllerModel(TestCase):
    def test_domain_controller_model(self):
        ip: str = '127.0.0.1'
        DomainController.set(ip=ip)
        dc: str = DomainController.get()
        self.assertIsNotNone(dc)
#
#
# class TestManagementCommands(TestCase):
#     def test_discovery(self) -> None:
#         """
#         Tests 'python manage.py discover' command
#         """
#         out = StringIO()
#         result = call_command('discover', stdout=out)
#         self.assertIsNone(result)
#         self.assertEqual(out.getvalue(), '')
#         dc: str = DomainController.get()
#         self.assertIsNotNone(dc)
#
#     @override_settings(DEBUG=True)
#     def test_logger(self) -> None:
#         out: StringIO = StringIO()
#         handler: logging.StreamHandler = logging.StreamHandler(stream=out)
#         logger.addHandler(hdlr=handler)
#         message: str = 'some test log message'
#         logger.error(message)
#         logger.removeHandler(hdlr=handler)
#         self.assertEqual(out.getvalue().rstrip(), message)
#
#
class TestADTools(TestCase):
    def test_clear_username(self):
        self.assertEqual(ad_clear_username('user@domain.com'), 'user')
        self.assertEqual(ad_clear_username('DOMAIN\\user'), 'user')

    def test_login(self):
        domain_controller_ip: str = '127.0.0.1'
        ldap_username: str = f'userspy@shmakovpn.ru'
        ldap_password: str = f'a-123456'
        ldap_conn = ldap_conn(dc=domain_controller_ip, username=ldap_username, password=ldap_password)
        if settings.ADTOOLS_TEST_USERNAME and settings.ADTOOLS_TEST_PASSWORD:
            conn = django_adtools.ad.ad_tools.ldap_connect(
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
#
#
