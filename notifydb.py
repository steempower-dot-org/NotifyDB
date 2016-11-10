import eventlet
eventlet.monkey_patch()
import json
import web
import dbstore
import config
import memcache
import pubsub
from config import chain
from eventlet import wsgi, websocket, greenpool

@websocket.WebSocketWSGI
def ws_handle_sub(ws):
    global pubsub_router
    path = ws.path.strip('/').split('/')[2]
    ws.send(path)
    while True:
       for msg in pubsub_router.subscribe(path):
           ws.send(json.dumps(msg))

class ws_error:
   def GET(self,name):
       return 'This should never happen, wtf?'

workpool = greenpool.GreenPool()

class blocks_handler:
   def _GET(self,by,which):
       global block_db
       if by=='by-id':
         block_data = block_db.get_block(block_id=which)
       elif by=='by-num':
         block_data = block_db.get_block(block_number=which)
       else:
         return web.notfound()
       
       if block_data == None:
          return web.notfound()
       return json.dumps(block_data)
   def GET(self,by,which):
       global mc
       web.header('Content-Type','application/json')
       retval = mc.get('GETBLOCK::%s::%s' % (by,which))
       if retval == None:
          retval = self._GET(by,which)
          mc.set('GETBLOCK::%s::%s' % (by,which),retval)
       return retval
   def POST(self):
       global block_db
       global workpool
       global pubsub_router
       data      = web.data()
       try:
          json_data  = json.loads(data)
          block_id   = json_data['id']
          block_num  = json_data['number']
          block_data = json_data['data']
       except:
          return web.badrequest()
       if block_id == '$':
          block_id = chain.gen_block_id(block_num,block_data)
       if not chain.valid_block(block_data):
          return web.badrequest()
       interested_parties = chain.get_interested_parties(block_data)
       for r in workpool.imap(lambda x: chain.notify_interested_party(block_data,x,pubsub_router),interested_parties):
           pass
       db_hash = block_db.store_block(block_data,block_num,block_id)
       return json.dumps({'id':block_id,'number':block_num,'db_hash':db_hash})


def dispatcher(environ, start_response):
    if environ['PATH_INFO'].startswith('/ws/sub'):
       return ws_handle_sub(environ, start_response)
    return web_app.wsgifunc()(environ,start_response)

if __name__=='__main__':
   urls = ('/ws/(.*)',                   'ws_error',
           '/blocks/(by-id|by-num)/(.*)','blocks_handler',
           '/blocks',                    'blocks_handler')

   mc       = memcache.Client(config.mc_endpoint)

   block_db = dbstore.BlockStore()
   
   pubsub_router = pubsub.Router()
   
   web_app = web.application(urls, globals())

   wsgi.server(eventlet.listen(('localhost', 12036)), dispatcher)
