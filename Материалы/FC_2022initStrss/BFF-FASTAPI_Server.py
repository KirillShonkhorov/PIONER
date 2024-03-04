import logging
import uvicorn
import httpx

from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect, WebSocketState
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from Logger import Logger

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.connections = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.add(websocket)
        logging.info('WebSocket connected')

    @staticmethod
    async def disconnect(websocket: WebSocket):
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
            logging.info('WebSocket disconnected')
        else:
            logging.info('WebSocket is already disconnected')

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
            logging.debug(f'WebSocket sent message "{message}"')
        except WebSocketDisconnect:
            self.connections.remove(websocket)
            await websocket.close()
            logging.warning('Client disconnected. Cleaned up')

    async def broadcast(self, message: str):
        for connection in self.connections:
            await self.send_message(message, connection)
            logging.debug(f'WebSocket broadcast sent a message "{message}"')


manager = ConnectionManager()


class BffFastAPI:
    def __init__(self, local_ip='localhost', port=8000):
        self.local_ip = local_ip
        self.port = port
        self.base_url = f"http://{local_ip}:5000/api/v1/jsonrpc/"
        self.templates = Jinja2Templates(directory="WebApplication/frontend/html")

    async def save_input_template(self, request: Request):
        data = await request.json()
        file_name = data.get("fileName")
        file_content = data.get("fileContent")

        in_params = {
            "in_file": {
                "fileName": file_name,
                "fileContent": file_content
            }
        }

        return await self.call_rpc("save_input_template", in_params)

    async def get_html(self, request: Request):
        logging.debug("****'get_html' request completed****")
        return self.templates.TemplateResponse("selectTemplate.html", {"request": request, "user_ip": self.local_ip, "user_port": self.port})

    async def websocket_endpoint(self, websocket: WebSocket):
        logging.debug("****Start processing the 'websocket_endpoint' request****")

        try:
            await manager.connect(websocket)
        except Exception as e:
            await manager.disconnect(websocket)
            logging.error(f"WebSocket was disconnected. Exception: {e}")

        try:
            while True:
                data = str(await websocket.receive_text())
                logging.info(f"Received data from WebSocket: {data}")

                in_params = {
                    "in_file": {
                        "fileName": data
                    }
                }

                rpc_data = str(await self.call_rpc("run_selected_template", in_params))
                await websocket.send_text(rpc_data)

        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            logging.warning("The client has disconnected. Cleaned up")
        except Exception as e:
            logging.error(f"WebSocket Exception: {e}")
        finally:
            logging.debug("****Finish processing the 'websocket_endpoint' request****")

    async def change_iteration_count(self, filename, iteration_count):
        in_params = {
            "in_file": {
                "fileName": filename
            }
        }

        rpc_data = str(await self.call_rpc("get_output_data", in_params))
        rpc_data = "Input parameter is not a string"

    async def call_rpc(self, method, in_params):
        logging.debug(f"****Start processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'")

        url = f"{self.base_url}{method}"
        headers = {'content-type': 'application/json'}

        loc_json_rpc = {
            "jsonrpc": "2.0",
            "id": "0",
            "method": method,
            "params": in_params
        }

        try:
            response = httpx.post(url, json=loc_json_rpc, headers=headers, timeout=0.1)
            response.raise_for_status()
            response_data = response.json()
            logging.debug(f'Response for RPC was completed')
        except Exception as e:
            logging.error(f'RPC connection exception: {e}')
            logging.debug(f"****Finish processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'")
            return f"RPC connection exception. Exception: {e}"

        if 'result' in response_data:
            logging.info(f"RPC response have a result '{response_data['result']}'")
            logging.debug(f"****Finish processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'")
            return response_data['result']
        else:
            logging.error("RPC response haven't a result")
            logging.debug(f"****Finish processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'")
            return f"RPC response haven't a result. Response description: {response_data}"


@app.get("/")
async def get_html(request: Request):
    return await bff_fastapi.get_html(request)


@app.get("/get_input_templates")
async def get_input_templates():
    return await bff_fastapi.call_rpc("get_input_templates", {})


@app.post("/save_input_template")
async def save_input_template(request: Request):
    return await bff_fastapi.save_input_template(request)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await bff_fastapi.websocket_endpoint(websocket)

if __name__ == '__main__':
    logger = Logger("Log", "BFF-FASTAPI_Server.log")
    bff_fastapi = BffFastAPI()

    app.mount("/static", StaticFiles(directory="WebApplication/frontend"), name="static")

    logging.debug("*****************BFF-FASTAPI server was started*****************")
    uvicorn.run(app, host=bff_fastapi.local_ip, port=bff_fastapi.port, access_log=True)
    logging.debug("*****************BFF-FASTAPI server was stopped*****************")
