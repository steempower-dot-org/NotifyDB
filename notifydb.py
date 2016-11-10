import eventlet
import json
import web
from eventlet import wsgi, websocket

@websocket.WebSocketWSGI
def ws_handle(ws):
    ws.wait()

class ws_error:
   def GET(self,name):
       return 'This should never happen, wtf?'

class blocks_handler:
   def GET(self,name=None):
       return ''

def dispatcher(environ, start_response):
    if environ['PATH_INFO'].startswith('/ws/'):
       return ws_handle(environ, start_response)
    return web_app.wsgifunc()(environ,start_response)

if __name__=='__main__':
   urls = ('/ws/(.*)',     'ws_error',
           '/blocks/(.*)', 'blocks_handler',
           '/blocks',      'blocks_handler')

   web_app = web.application(urls, globals())

   wsgi.server(eventlet.listen(('localhost', 12036)), dispatcher)
