import sys
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import Union
import asyncio

import requests
import json

# loc_ip = "192.168.1.181"
loc_ip = "localhost"

# loc_ip = "localhost"

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <input type="text" id="inputVar" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            const dialog = document.getElementById("myDialog"); 
        
            //var ws = new WebSocket("ws://192.168.0.20:8000/ws");
            var ws = new WebSocket("ws://""" + loc_ip + """:8000/ws");
            ws.onmessage = function(event) {

                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)

                if (content.wholeText == 'clear')
                {
                    while (messages.firstChild) messages.removeChild(messages.firstChild);
                }else{
                message.appendChild(content)
                messages.appendChild(message)
                window.scrollTo(0, document.body.scrollHeight);
                }
            };  
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                var input2 = document.getElementById("inputVar")
                ws.send(input.value + ' ' + input2.value)
                //input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    last_message = ""

    def __init__(self) -> None:
        self.connections = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections = websocket

    async def disconnect(self):
        if self.connections is not None:
            websocket: WebSocket = self.connections
            await websocket.close()
        self.connections = None
        print('web socket disconnect')

    async def send_messages(self, message):
        if self.connections is not None:
            websocket: WebSocket = self.connections
            try:
                await websocket.send_text(message)
            except websocket.exceptions.ConnectionClosed:
                print("Client disconnected.  Do cleanup")


cnt = 0
manager = ConnectionManager()


def call_rpc(tag, rpc_digit_param):
    url = "http://localhost:5000/api/v1/jsonrpc"
    headers = {'content-type': 'application/json'}

    loc_json_rpc = {"jsonrpc": "2.0",
                    "id": "0",
                    "method": "echo",
                    "params": {"in_params": {
                        "tag": tag,
                        "x": rpc_digit_param
                    }}
                    }

    try:
        response = requests.post(url, data=json.dumps(loc_json_rpc), headers=headers, timeout=0.1)
    except Exception as err:
        print('rpc connection exception')
        return {'datas': 'error connection'}

    # print('res ', response.status_code)
    # print('text ', response.text)
    if response.status_code == 200:
        response = response.json()

        if ('result' in response):
            return response['result']
        else:
            return {'datas': 'error fnc not found'}
    else:
        print('status code is not 200')
        return {'datas': 'error response'}


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.get("/ping_old")
async def get(tag: Union[str, None] = 'square', letter: Union[str, None] = 'nofing', dig: Union[float, None] = 0):
    global cnt
    cnt = cnt + 1
    res = {'response': str(dig) + " -> " + letter + " -> " + str(cnt)}
    try:
        await manager.send_messages(str(res))
    except Exception as err:
        print('web socket is closed')
    return res


@app.get("/rpc_old")
async def get(tag: Union[str, None] = 'square', letter: Union[str, None] = 'nothing', dig: Union[float, None] = 0):
    res = {'response': 'what a hell is going on??!', 'tag': tag,
           'letter': letter + ' ' + str(call_rpc(tag, dig)['datas'])}
    if tag == 'clear':
        global cnt
        cnt = 0
        await manager.send_messages("clear")
    else:
        await manager.send_messages(str(res))
    return res


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # await websocket.accept()
    try:
        await manager.connect(websocket)
    except:
        await manager.disconnect()

    while True:
        # data = await websocket.receive_text()
        try:
            data = await manager.connections.receive_text()
        except Exception as err:
            print('cant recive text')
            return

        rpc_input_var = data.split(" ")[1]
        data = data.split(" ")[0]
        # print('data ', type(rpc_input_var), rpc_input_var)

        try:
            rpc_input_var = float(rpc_input_var)
        except Exception as err:
            rpc_input_var = 'inpurt param is not digit'
            print('Exception of response type', rpc_input_var)

        if (isinstance(rpc_input_var, float)):
            rpc_data = call_rpc("square", rpc_input_var)['datas']
        else:
            rpc_data = 'inpurt param is not digit'

        data = data + ' ' + str(rpc_data)
        try:
            await websocket.send_text(f"hello Message text was: {data}")
        except Exception as err:
            print('cant send text')


if __name__ == '__main__':
    import uvicorn

    # uvicorn.run('bff_fastapi:app', host=loc_ip, port=8000, access_log=False, reload=False, workers=3)
    uvicorn.run('bff_fastapi:app', host=loc_ip, port=8000, access_log=False, reload=True)
    # uvicorn.run('bff_fastapi:app',  port=8000, access_log=False)
