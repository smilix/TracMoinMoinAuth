# -*- coding: utf-8 -*-
#
# Manages user accounts stored in MoinMoin user directory.
# Author: HolgerCremer@gmail.com


from os import listdir, stat
from os.path import join, exists
import re

from passlib.context import CryptContext


class MoinMoinUserDir():
    USER_FILE_RE = re.compile(r'^[0-9\.]+$')

    def __init__(self, logger, mm_user_dir, disable_cache):
        if mm_user_dir is None:
            raise ValueError('No "mm_user_dir" configuration.')
        if not exists(mm_user_dir):
            raise ValueError('mm_user_dir "%s" doesn`t exist!' % mm_user_dir)

        self._crypt_context = CryptContext(
            # is the default value in the MoinMoin wiki
            schemes=['sha512_crypt', ]
        )

        self._log = logger
        self._mm_user_dir = mm_user_dir
        self._disable_cache = disable_cache

        self._user_cache = None
        self._user_cache_check = None

    def get_users(self):
        users = self._list_users_and_pw()
        user_list = []
        for name in users:
            user_list.append(name)

        return user_list

    def check_password(self, user, password):
        users = self._list_users_and_pw()
        for name in users:
            if name == user:
                pw_correct = self._crypt_context.verify(password, users[name])
                self._log.info('User %s found, pw check success: %s' % (name, pw_correct))
                return pw_correct

        return None

    def _list_users_and_pw(self):
        if not self._must_read_again():
            return self._user_cache

        self._log.debug('read user data again')
        users = {}
        for user_file in listdir(self._mm_user_dir):
            if self.USER_FILE_RE.match(user_file) is None:
                continue
            (name, password) = self._get_name_and_password(user_file)
            if name is None:
                continue
            name = name.decode('utf8')
            users[name] = password

        self._user_cache = users
        return users

    def _must_read_again(self):
        if self._disable_cache:
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
        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = stat(self._mm_user_dir)
        return '%s-%s-%s-%s' % (size, atime, mtime, ctime)

    def _get_name_and_password(self, file_name):
        name_prefix = 'name='
        pw_prefix = 'enc_password='
        scheme_prefix = '{PASSLIB}'
        name, password = None, None
        with open(join(self._mm_user_dir, file_name), "r") as file:
            for line in file:
                if line.startswith(name_prefix):
                    # remove prefix and newline
                    name = line[len(name_prefix):len(line) - 1]
                elif line.startswith(pw_prefix):
                    # remove prefix and newline
                    password = line[len(pw_prefix):len(line) - 1]
                    # check for passlib prefix
                    if not password.startswith(scheme_prefix):
                        self._log.warn('Unsupported scheme prefix. User "%s" won\'t login.' % file_name.encode('utf8', 'ignore'))
                        return None, None
                    # remove the scheme prefix
                    password = password[len(scheme_prefix):]

                if name is not None and password is not None:
                    return name, password

        self._log.warn('No %s and %s entries found for file %s.' % (name_prefix, pw_prefix, file_name.encode('utf8', 'ignore')))
        return None, None


