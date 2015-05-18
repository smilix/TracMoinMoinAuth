# -*- coding: utf-8 -*-
#
# Get the user data from the https://github.com/smilix/moinAuthProvider action.
# Author: HolgerCremer@gmail.com

import requests
from requests.packages.urllib3 import PoolManager


class MoinMoinAuthByProvider():
    def __init__(self, logger, provider_url, psk, ssl_fingerprint, ca_certs, disable_cache):
        if provider_url is None or provider_url == "":
            raise ValueError('No "provider_url" configuration.')
        if psk is None or psk == "":
            raise ValueError('No "psk" configuration.')

        self._provider_url = provider_url
        self._psk = psk
        self._ssl_fingerprint = ssl_fingerprint
        self._ca_certs = ca_certs
        # ToDo: implement
        self._disable_cache = disable_cache

        self._session = requests.Session()
        fingerprint_adapter = _FingerprintAdapter(self._ssl_fingerprint)
        self._session.mount("https://", fingerprint_adapter)

    def get_users(self):
        result = self._make_request("list")
        user_list = []
        for user in result:
            user_list.append(user["login"])

        return user_list


    def check_password(self, user, password):
        result = self._make_request("loginCheck", {
            "login": user,
            "password": password
        })

        if result["result"] == "ok":
            return True
        elif result["result"] == "wrong_password":
            return False
        else:
            return None


    def _make_request(self, do_type, json=None):
        if not json:
            json = {}
        url = self._provider_url + "?action=authService&do=" + do_type
        resp = self._session.post(url, headers={
            "Auth-Token": self._psk
        }, json=json, verify=self._ca_certs)
        if resp.status_code != 200:
            raise StandardError("Unexpected response code %d for '%s'. \nServer response was: %s" % (resp.status_code, url, resp.text))

        return resp.json()


# from https://github.com/untitaker/vdirsyncer/blob/9d3a9611b2db2e92f933df30dd98c341a50c6211/vdirsyncer/utils/__init__.py#L198
class _FingerprintAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, fingerprint=None, **kwargs):
        self.fingerprint = str(fingerprint)
        super(_FingerprintAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       assert_fingerprint=self.fingerprint)

