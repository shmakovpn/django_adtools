"""
django_adtools/ad_tools.py

Some tools to use

REQUIREMENTS:
   pip install python-ldap  # on linux
   # on Windows download compiled package for your system from https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap
"""
__author__ = "shmakovpn <shmakovpn@yandex.ru>"
__date__ = "2020-04-15"

import re
import ldap
import ldap.filter  # escaping character in ldap requests
import logging
# type hints
from typing import TypeVar, List, Tuple, Dict
LdapSearchResult = List[Tuple[str, Dict[str, List[bytes]]]]  # the type of an ldap search result
LDAP_CONNECTION = TypeVar('LDAP_CONNECTION', ldap.ldapobject.SimpleLDAPObject, type(None))

domain_suffix_pattern = re.compile(r'@.*$')  #: pattern for domain suffix
domain_prefix_pattern = re.compile(r'^[^\\]*\\')  #: patter for domain prefix

#: logger for this __package__
logger = logging.getLogger(__package__)


def ad_clear_username(username: str) -> str:
    """
    Removes domain suffix and prefix from the username

    :param username: active directory username
    :type username: str
    :return: cleared username without domain suffix and prefix
    :rtype: str
    """
    username = domain_suffix_pattern.sub('', username)
    username = domain_prefix_pattern.sub('', username)
    return username


def ldap_connect(dc: str, username: str, password: str) -> LDAP_CONNECTION:
    """
    Inits ldap connection, binds to ldap using username and password, returns ldap connection if binding was ok

    :param dc: an ip address of domain controller
    :type dc: str
    :param username: an active directory username
    :type username: str
    :param password: an active directory user password
    :type password: str
    :return: ldap connection if binding was ok, None otherwise
    :rtype: ldap.ldapobject.SimpleLDAPObject
    """
    ldap_connection: ldap.ldapobject.SimpleLDAPObject = ldap.initialize('ldap://%s' % dc)
    # ldap_connection.protocol_version = 3
    ldap_connection.set_option(ldap.OPT_REFERRALS, 0)
    # ldap_connection.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    try:
        ldap_connection.bind_s(username, password)
        return ldap_connection
    except ldap.INVALID_CREDENTIALS:
        logger.warning(f'{__package__} ldap_connect failed, ldap.INVALID_CREDENTIALS '
                       f'dc={dc}, username={username}, password={password}')
        return None
    except ldap.SERVER_DOWN:
        logger.error(f'{__package__} ldap_connect failed, ldap.SERVER_DOWN dc={dc}')
        return None


def user_dn(conn: ldap.ldapobject.SimpleLDAPObject, username: str, domain: str) -> str:
    """
    Requests user DN from active directory by username

    :param conn: established connection to domain controller
    :type conn: ldap.ldapobject.SimpleLDAPObject
    :param username: an active directory username
    :type username: str
    :param domain: full name of active directory domain
    :type domain: str
    :return: distinguished name for username if success, empty string otherwise
    :rtype: str
    """
    if not conn:
        logger.error(f'{__package__} user_dn failed "conn" is null')
        return ''
    ldap_base: str = ','.join('dc=%s' % x for x in domain.split('.'))
    search_filter: str = '(|(&(objectClass=person)(sAMAccountName=%s)))' % ad_clear_username(username)
    try:
        results: List[str] = list(
            filter(lambda x: x[0] is not None, conn.search_s(ldap_base, ldap.SCOPE_SUBTREE, search_filter, ['']))
        )
        if not len(results):
            logger.warning(f'{__package__} user_dn failed:'
                           f' results is empty, ldap_base={ldap_base}, search_filter={search_filter}')
            return ''
        return results[0][0]
    except ldap.OPERATIONS_ERROR as e:
        logger.error(f'{__package__} user_dn failed:'
                     f' {str(e)}, ldap_base={ldap_base}, search_filter={search_filter}')
        return ''


def dn_groups(conn: ldap.ldapobject.SimpleLDAPObject, dn: str, domain: str) -> List[str]:
    """
    Request group names from active directory by user DN

    :param conn: established connection to domain controller
    :type conn: ldap.ldapobject.SimpleLDAPObject
    :param dn: an active directory user DN
    :type dn: str
    :param domain: full name of active directory domain
    :type domain: str
    :return: list of group names whose user with DN is member of (SUCCESS), empty list otherwise
    :rtype: List[str]
    """
    if not conn:
        logger.error(f'django_adtool.ad.ad_tools dn_groups failed. "conn" is null. dn={dn}, domain={domain}')
        return []
    ldap_base: str = ','.join('dc=%s' % x for x in domain.split('.'))
    search_filter: str = '(|(&(objectClass=group)(member=%s)))' % ldap.filter.escape_filter_chars(dn)
    try:
        results: LdapSearchResult = list(
            filter(
                lambda x: x[0] is not None,
                conn.search_s(ldap_base, ldap.SCOPE_SUBTREE, search_filter, ['sAMAccountName'])
            )
        )
        if not results:
            logger.error(f'{__package__} dn_group failed. results is empty, dn={dn}, domain={domain}')
        return [item[1]['sAMAccountName'][0].decode() for item in results]
    except ldap.OPERATIONS_ERROR as e:
        logger.error(f'{__package__} dn_group failed: {str(e)}, dn={dn}, domain={domain}')
        return []


def ad_login(dc: str, username: str, password: str, domain: str, group: str) -> bool:
    """
    Returns true if the user can log in and is included in the desired group

    :param dc: hostname or ip address of a domain controller
    :type dc: str
    :param username:
    :type username: str
    :param password:
    :type password: str
    :param domain: a name of domain, e.g. example.com
    :type domain: str
    :param group: a name of valid domain group, if an user is in this group, then it can log in
    :type group: str
    :return: true if the user can log in and is included in the desired group
    :rtype: bool
    """
    if not dc:
        logger.error(f'{__package__} ad_login failed. "dc" is null')
        return False
    conn = ldap_connect(
        dc=dc,
        username=username,
        password=password,
    )
    if not conn:
        logger.error(f'{__package__} ad_login failed.'
                     f' "ldap_connect" failed dc={dc}, username={username}, password={password}')
        return False
    dn = user_dn(
        conn=conn,
        username=username,
        domain=domain,
    )
    if not dn:
        logger.error(f'{__package__} ad_login failed.'
                     f' "user_dn" failed dc={dc}, username={username}, password={password}')
        return False
    groups = dn_groups(
        conn=conn,
        dn=dn,
        domain=domain,
    )
    if not groups:
        logger.error(f'{__package__} ad_login failed.'
                     f' "dn_goups" failed dc={dc}, username={username}, password={password}')
        return False
    if not group or group in groups:
        return True  # user is authenticated
    else:
        logger.error(f'{__package__} ad_login failed.'
                     f' group={groups} not in {groups}.  dc={dc}, username={username}, password={password}')
        return False
