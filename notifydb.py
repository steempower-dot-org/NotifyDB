import eventlet
eventlet.monkey_patch()
import json
import web
import dbstore
import config
import memcache
import pubsub
from eventlet import wsgi, websocket

@websocket.WebSocketWSGI
def ws_handle_sub(ws):
    global pubsub_router
    for msg in pubsub_router.subscribe('test'):
        print msg
        ws.send(msg)

@websocket.WebSocketWSGI
def ws_handle_pub(ws):
    global pubsub_router
    while True:
       m = ws.wait()
       pubsub_router.publish('test',m)

class ws_error:
   def GET(self,name):
       return 'This should never happen, wtf?'

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
       data      = web.data()
       try:
          json_data  = json.loads(data)
          block_id   = json_data['id']
          block_num  = json_data['number']
          block_data = json_data['data']
       except:
          return web.badrequest()


def dispatcher(environ, start_response):
    if environ['PATH_INFO'].startswith('/ws/sub'):
       return ws_handle_sub(environ, start_response)
    elif environ['PATH_INFO'].startswith('/ws/pub'):
       return ws_handle_pub(environ, start_response)
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
