# TracMoinMoinAuth

Using the MoinMoin wiki user database for trac authentication.

# Prerequisite

* This plugin needs the http://trac-hacks.org/wiki/AccountManagerPlugin to be installed.
* For the "dir" auth method you need the ```passlib``` python lib. For "auth_provider" you need ```requests``` python lib.
 

# Install

* Run in this directory (that with the `setup.py`):
```
python setup.py bdist_egg
```
* Copy the resulting .egg file to your `trac/env/plugins/` folder. 
* Update your `trac.ini`
```
    [account-manager]
    password_store = MoinMoinPasswordStore

    [moinmoinauth]
    mm_auth_method = auth_provider
    mm_auth_provider_url = https://your_wiki.abc
    mm_auth_provider_psk = your_password
    mm_auth_provider_fingerprint = 12345sha1
    # optional
    mm_auth_provider_ca_certs = /path/to/certs.pem 
    # or for 
    # mm_auth_method = dir 
    # you need 
    # mm_user_dir = /path/to/moinmoin/users

    [components]
    acct_mgr.web_ui.loginmodule = enabled
    acct_mgr.web_ui.registrationmodule = disabled
    trac.web.auth.loginmodule = disabled
```
