""" Imports blockchain from a steemd node
"""

import config
import json
import requests
import websocket

ws = websocket.WebSocket()
ws.connect(config.steemd_endpoint)
ws.send('{"id":1,"method":"get_dynamic_global_properties","params":[]}')
resp = ws.recv()

resp_data = json.loads(resp)

head_block_no = resp_data['result']['head_block_number']

for x in xrange(1,head_block_no):
    ws.send('{"id":%s,"method":"get_block","params":["%s"]}' % (x+1,x))
    resp        = ws.recv()
    resp_data   = json.loads(resp)['result']
    upload_data = {'id':'$','number':str(x),'data':resp_data}
    req         = requests.post('http://localhost:12036/blocks',json=upload_data)
    print req.json()
