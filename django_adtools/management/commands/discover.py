"""
django_adtools/management/commands/discover.py
Discovers Domain Controllers
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-05'

import os
from django.core.management.base import BaseCommand
from django_adtools.models import DomainController
from django_adtools.dns.discover_dc import DCList
from django.conf import settings
from typing import List

role: str = getattr(settings, 'ADTOOLS_ROLE', 'dc')  #: domain controller server role
domain: str = getattr(settings, 'ADTOOLS_DOMAIN')  #: ad realm
name_servers: List[str] = getattr(settings, 'ADTOOLS_NAMESERVERS', None)  #: list of ip of dns servers
if os.name == 'nt' and not name_servers:
    raise RuntimeError("'ADTOOLS_NAMESERVERS' does not present in settings.py on Windows")


class Command(BaseCommand):
    """
    Discovers Domain Controllers, saves found controller into DomainController model
    """
    help = """Discovers Domain Controllers, saves found controller into DomainController model"""

    def handle(self, *args, **kwargs) -> None:
        """
        Perform dns requests
        """
        ip: str = DCList(domain=domain, role=role, nameservers=name_servers).get_available_dc_ip()
        DomainController.set(ip)
