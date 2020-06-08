"""
django_adtools/models.py
"""
__author__ = 'shmakovpn <shmakovpn@yandex.ru>'
__date__ = '2020-06-05'

from django.db import models


# Create your models here.
class DomainController(models.Model):
    """
    Model for storing the ip address of an available domain controller
    """
    ip = models.CharField(max_length=15, null=False)

    @classmethod
    def get(cls) -> str:
        """
        Returns an ip address of Domain Controller or '' if it does not exist
        :return: an ip address of Domain Controller
        :rtype: str
        """
        try:
            return cls.objects.all()[0].ip
        except DomainController.DoesNotExist:
            return ''
        except IndexError:
            return ''

    @classmethod
    def set(cls, ip: str) -> None:
        """
        Sets the ip address of domain controller
        :param ip: an ip address of domain controller
        :return: None
        """
        cls.objects.all().delete()
        dc: DomainController = cls()
        dc.ip = ip
        dc.save()
