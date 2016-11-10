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

REST API, use JSON dicts to represent blocks

/blocks/by-id/<blockID>       represents a single block by ID, HTTP GET only

/blocks/by-num/<blockNumber>  represents a single block by block number, HTTP GET only

/blocks can accept a POST to create a new block, the body must be JSON and consist of these fields: id,number,data

If the id field is set to the string "$" then the server will assign an ID to the block


For websockets:

/ws/blocks                   gets a stream of blocks as they come in

/ws/votes                    gets a stream of ALL votes as they come in

/ws/comments                 gets a stream of ALL comments as they come in

To refine websockets stream you can subscribe to single relevant feeds by keyword

e.g

 /ws/sub/<keyword>

 /ws/sub/steempower

   will send all transaction ops that reference steempower


Backups etc:

Data is stored locally in whatever the current working directory is with no attempt whatsoever to make
the file format portable. If you want to move your data elsewhere you MIGHT get lucky with just
copying it over, but this is not recommended - instead, dump it and then reload it.


Security:

You are advised to never modify this code to bind to a remotely accessible endpoint and you should never use data files from an untrusted source (in fact, as above - don't share them between machines at all).
