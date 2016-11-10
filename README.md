Designed for use with blockchains (and developed for use on SteemPower.org), NotifyDB is a NoSQL
database platform with integrated notifications.

Feed it blocks, and then it populates the database while sending notifications to specified endpoints.

Dependencies:

 * eventlet
 * python websocket - if you want to load blocks from steem
 * web.py - see webpy.org
 * memcached - see https://pypi.python.org/pypi/python-memcached

Setup:

First, make sure memcached is running, next just run notifydb.py, by default it'll bind to localhost:12036 to avoid clashing with any other services.

Usage:

It's a REST API, POST blocks as json to http://localhost:12036/blocks

Backups etc:

Data is stored locally in whatever the current working directory is with no attempt whatsoever to make
the file format portable. If you want to move your data elsewhere you MIGHT get lucky with just
copying it over, but this is not recommended - instead, dump it and then reload it.


Security:

You are advised to never modify this code to bind to a remotely accessible endpoint and you should never use data files from an untrusted source (in fact, as above - don't share them between machines at all).
