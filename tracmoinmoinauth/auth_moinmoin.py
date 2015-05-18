# -*- coding: utf-8 -*-
#
# Manages users from MoinMoin
# Author: HolgerCremer@gmail.com
#

from trac.core import Component, implements
from trac.config import Option, BoolOption

from acct_mgr.api import IPasswordStore
from moinmoin_auth_by_provider import MoinMoinAuthByProvider
from moinmoin_user_dir import MoinMoinUserDir


class MoinMoinPasswordStore(Component):
    implements(IPasswordStore)

    mm_auth_method = Option('moinmoinauth', 'mm_auth_method', doc='"dir" or "auth_provider"')
    mm_auth_provider_url = Option('moinmoinauth', 'mm_auth_provider_url',
                                  doc='The url to the ..... If set, this has priority over the mm_user_dir option.')
    mm_auth_provider_psk = Option('moinmoinauth', 'mm_auth_provider_psk', doc='The psk/key for the auth service.')
    mm_auth_provider_fingerprint = Option('moinmoinauth', 'mm_auth_provider_fingerprint',
                                          doc='The fingerprint for the ssl certificate of the auth service.')
    mm_auth_provider_ca_certs = Option('moinmoinauth', 'mm_auth_provider_ca_certs',
                                          doc='File with custom ca certificates.')
    mm_user_dir = Option('moinmoinauth', 'mm_user_dir', doc='The MoinMoin users directory')
    disable_cache = BoolOption('moinmoinauth', 'disable_cache', default=False,
                               doc='Caches (as default) the user data from the MoinMoin user directory or the server response.')

    def __init__(self):
        if self.mm_auth_method == 'dir':
            self._user_impl = MoinMoinUserDir(self.log, self.mm_user_dir, self.disable_cache)
        elif self.mm_auth_method == 'auth_provider':
            self._user_impl = MoinMoinAuthByProvider(self.log, self.mm_auth_provider_url, self.mm_auth_provider_psk,
                                                     self.mm_auth_provider_fingerprint, self.mm_auth_provider_ca_certs, self.disable_cache)
        else:
            raise ValueError('Unknown value "%s" for mm_auth_method. Use "dir" or "auth_provider"' % self.mm_auth_method)

    def has_user(self, user):
        return user in self._user_impl.get_users()

    def get_users(self):
        self.log.debug('getting user list...')
        return self._user_impl.get_users()

    def check_password(self, user, password):
        self.log.info('acct_mgr: checking password for %s ' % user)
        if self._is_user_ignored(user):
            return None

        return self._user_impl.check_password(user, password)

    def set_password(self, user, password, old_password=None):
        raise NotImplementedError

    def delete_user(self, user):
        raise NotImplementedError

    def _is_user_ignored(self, username):
        if username is None:
            return True
        # ignore the default build-in groups
        if username == 'authenticated' or username == 'anonymous':
            return True
        # our groups start with '__group__'
        return username.startswith('__group__')
