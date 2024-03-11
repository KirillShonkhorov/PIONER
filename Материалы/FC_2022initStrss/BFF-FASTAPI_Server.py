import logging
import uvicorn
import httpx

from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect, WebSocketState
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from Logger import Logger

app = FastAPI()


class ErrorModel(BaseModel):
    details: str
    status_code: int


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
        app.mount("/static", StaticFiles(directory="WebApplication/frontend"), name="static")

    async def save_input_template(self, request: Request):
        try:
            logging.debug("\t****Start processing the 'save_input_template' request****\t")

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

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return ErrorModel(details=f"BFF-FASTAPI server error : {error}", status_code=501)
        finally:
            logging.debug("\t****Finish processing the 'save_input_template' request****\t")

    async def get_html(self, request: Request):
        try:
            logging.debug("\t****Start processing the 'get_html' request****\t")
            return self.templates.TemplateResponse("selectTemplate.html", {"request": request, "user_ip": self.local_ip, "user_port": self.port})
        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return ErrorModel(details=f"BFF-FASTAPI server error : {error}", status_code=500)
        finally:
            logging.debug("\t****Finish processing the 'get_html' request****\t")

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

                rpc_data = await self.call_rpc("run_selected_template", in_params)

                print(rpc_data)

                await websocket.send_text(rpc_data)

        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            logging.warning("The client has disconnected. Cleaned up")
        except Exception as e:
            logging.error(f"WebSocket Exception: {e}")
        finally:
            logging.debug("****Finish processing the 'websocket_endpoint' request****")

    async def call_rpc(self, method, in_params):
        try:
            logging.debug(f"\t****Start processing the 'call_rpc' request.****\t\nMethod: '{method}'\nInput Params:\n'{in_params}'\n")

            url = f"{self.base_url}{method}"
            headers = {'content-type': 'application/json'}

            loc_json_rpc = {
                "jsonrpc": "2.0",
                "id": "0",
                "method": method,
                "params": in_params
            }

            response = httpx.post(url, json=loc_json_rpc, headers=headers)
            response.raise_for_status()
            response_data = response.json()
            logging.debug(f'Response for RPC was completed')

            if 'result' in response_data:
                logging.info(f"RPC response have a result:\n'{response_data['result']}'")
                return response_data['result']
            else:
                logging.error("RPC response haven't a result")
                return f"RPC response haven't a result. Response description: {response_data}"

        except Exception as e:
            logging.error(f'BFF-FASTAPI server error. RPC connection exception: {e}')
            return f'BFF-FASTAPI server error. RPC connection exception: {e}'
        finally:
            logging.debug(f"****\tFinish processing the 'call_rpc' request.****\t\nMethod: '{method}'\nInput Params:\n'{in_params}'\n")


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

    logging.debug("+++++++++++++++++++++++++BFF-FASTAPI server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=bff_fastapi.local_ip, port=bff_fastapi.port, access_log=True)
    logging.debug("-------------------------BFF-FASTAPI server was stopped-------------------------")
