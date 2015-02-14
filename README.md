# TracMoinMoinAuth

Using the MoinMoin wiki user database for trac authentication.

# Prerequisite

* This plugin needs the http://trac-hacks.org/wiki/AccountManagerPlugin to be installed.
* You also have to install the passlib python lib. 

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
    mm_user_dir = /path/to/moinmoin/users

    [components]
    acct_mgr.web_ui.loginmodule = enabled
    acct_mgr.web_ui.registrationmodule = disabled
    trac.web.auth.loginmodule = disabled
```
