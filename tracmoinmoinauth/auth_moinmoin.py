# -*- coding: utf-8 -*-
#
# Manages user accounts stored in MoinMoin user directory.
# Author: HolgerCremer@gmail.com
#
from os import listdir, stat
from os.path import join, exists
import re

from passlib.context import CryptContext

from trac.core import Component, implements
from trac.config import Option, BoolOption

from acct_mgr.api import IPasswordStore


class MoinMoinPasswordStore(Component):
    implements(IPasswordStore)

    USER_FILE_RE = re.compile(r'^[0-9\.]+$')

    mm_user_dir = Option('moinmoinauth', 'mm_user_dir', doc='The MoinMoin users directory')
    disable_cache = BoolOption('moinmoinauth', 'disable_cache', default=False,
                               doc='Caches (as default) the user data from the MoinMoin user directory.')

    def __init__(self):
        if self.mm_user_dir is None:
            raise ValueError('No "mm_user_dir" configuration.')
        if not exists(self.mm_user_dir):
            raise ValueError('mm_user_dir "%s" doesn`t exist!' % self.mm_user_dir)

        self._crypt_context = CryptContext(
            # is the default value in the MoinMoin wiki
            schemes=['sha512_crypt', ]
        )

        self._user_cache = None
        self._user_cache_check = None

    def has_user(self, user):
        return self._read_users().has_key(user)

    def get_users(self):
        self.log.debug('getting user list...')
        usernames = []
        for name in self._read_users():
            usernames.append(name)

        return usernames

    def check_password(self, user, password):
        self.log.debug('acct_mgr: checking password for %s ' % user)
        if self._is_user_ignored(user):
            return None

        users = self._read_users()
        for name in users:
            if name == user:
                self.log.debug('User %s found, checking pw.' % name)
                return self._crypt_context.verify(password, users[name])

        return None

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

    def _must_read_again(self):
        if self.disable_cache:
            return True

        if self._user_cache is None or self._user_cache_check is None:
            self._user_cache_check = self._get_dir_check_value()
            return True

        new_check = self._get_dir_check_value()
        if new_check == self._user_cache_check:
            return False
        self._user_cache_check = new_check
        return True

    def _get_dir_check_value(self):
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = stat(self.mm_user_dir)
        return '%s-%s-%s-%s' % (size, atime, mtime, ctime)

    def _read_users(self):
        if not self._must_read_again():
            return self._user_cache

        self.log.debug('read user data again')
        users = {}
        for file in listdir(self.mm_user_dir):
            if self.USER_FILE_RE.match(file) is None:
                continue
            (name, password) = self._get_name_and_password(file)
            if name is None:
                continue
            if self._is_user_ignored(name):
                continue
            users[name] = password

        self._user_cache = users
        return users


    def _get_name_and_password(self, file_name):
        name_prefix = 'name='
        pw_prefix = 'enc_password='
        scheme_prefix = '{PASSLIB}'
        name, password = None, None
        with open(join(self.mm_user_dir, file_name), "r") as file:
            for line in file:
                if line.startswith(name_prefix):
                    # remove prefix and newline
                    name = line[len(name_prefix):len(line) - 1]
                elif line.startswith(pw_prefix):
                    # remove prefix and newline
                    password = line[len(pw_prefix):len(line) - 1]
                    # check for passlib prefix
                    if not password.startswith(scheme_prefix):
                        self.log.warn('Unsupported scheme prefix. User "%s" won´t login.' % file_name.encode('utf8', 'ignore'))
                        return (None, None)
                    # remove the scheme prefix
                    password = password[len(scheme_prefix):]

                if name is not None and password is not None:
                    return (name, password)

        self.log.warn('No %s and %s entries found for file %s.' % (name_prefix, pw_prefix, file_name.encode('utf8', 'ignore')))
        return (None, None)
