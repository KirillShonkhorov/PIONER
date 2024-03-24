import json
import logging
import uvicorn
import httpx
import netifaces
import asyncio

from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from Logger import Logger
from PydanticModels import Error
from WebsocketManager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


class BffFastAPI:
    def __init__(self, rpc_server_url, local_ip='localhost', port=8000):
        self.local_ip = asyncio.run(self.get_local_ip(local_ip))
        self.port = port
        self.rpc_server_url = f"http://{rpc_server_url}/api/v1/jsonrpc/"
        self.templates = Jinja2Templates(directory="WebApplication/frontend/html")
        app.mount("/static", StaticFiles(directory="WebApplication/frontend"), name="static")

    @staticmethod
    async def get_local_ip(local_ip):
        if local_ip == 'localhost':
            interfaces = netifaces.interfaces()
            for interface in interfaces:
                addresses = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addresses:
                    for address_info in addresses[netifaces.AF_INET]:
                        if 'addr' in address_info:
                            ip_address = address_info['addr']
                            if ip_address.startswith('192.168.'):
                                return ip_address

            return local_ip  # Если не найдено подходящего IP-адреса, вернуть localhost

        return local_ip  # Если указан явный IP-адрес, вернуть его

    async def delete_input_template(self, request: Request):
        try:
            logging.info("****Start processing the 'delete_input_template' request****")

            data = await request.json()
            file_name = data.get("fileName")

            in_params = {
                "in_file": {
                    "fileName": file_name,
                }
            }

            if await self.call_rpc("delete_input_template", in_params):
                logging.debug("Request return: True")
                return True
            else:
                logging.debug("Request return: False")
                return False

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 502})
        finally:
            logging.info("****Finish processing the 'delete_input_template' request****")

    async def save_input_template(self, request: Request):
        try:
            logging.info("****Start processing the 'save_input_template' request****")

            data = await request.json()
            file_name = data.get("fileName")
            file_content = data.get("fileContent")

            in_params = {
                "in_file": {
                    "fileName": file_name,
                    "fileContent": file_content
                }
            }

            result = await self.call_rpc("save_input_template", in_params)
            logging.debug(f"Request return: {result}")
            return result is None

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 503})
        finally:
            logging.info("****Finish processing the 'save_input_template' request****")

    async def get_html(self, request: Request):
        try:
            logging.info("****Start processing the 'get_html' request****")
            return self.templates.TemplateResponse("selectTemplate.html", {"request": request, "user_ip": self.local_ip, "user_port": self.port})
        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 500})
        finally:
            logging.info("****Finish processing the 'get_html' request****")

    async def websocket_endpoint(self, websocket: WebSocket):
        logging.info("****Start processing the 'websocket_endpoint' request****")

        try:
            await manager.connect(websocket)
        except Exception as error:
            await manager.disconnect(websocket)
            logging.exception(f"WebSocket was disconnected. Exception: {error}")

        try:
            while True:
                data = await websocket.receive_text()
                logging.debug(f"Received data from WebSocket: {data}")

                in_params = {
                    "in_file": {
                        "fileName": data
                    }
                }

                rpc_data = await self.call_rpc("run_selected_template", in_params)

                await websocket.send_text(json.dumps(rpc_data))

        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            logging.exception("The client has disconnected. Cleaned up")
        except Exception as e:
            logging.exception(f"WebSocket Exception: {e}")
        finally:
            logging.info("****Finish processing the 'websocket_endpoint' request****")

    async def call_rpc(self, method, in_params):
        try:
            logging.info(f"****Start processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'\n")

            url = f"{self.rpc_server_url}{method}"

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
                logging.debug(f"RPC response have a result:\n'{response_data['result']}'")
                return response_data['result']
            else:
                logging.warning("RPC response haven't a result!")
                return Error(data={'details': f"RPC response haven't a result. Response description: {response_data}", 'status_code': 400})

        except Exception as error:
            logging.exception(f'BFF-FASTAPI server error. RPC connection exception: {error}')
            return Error(data={'details': f"BFF-FASTAPI server error. RPC connection exception: {error}", 'status_code': 501})
        finally:
            logging.info(f"****Finish processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'\n")


@app.get("/")
async def get_html(request: Request):
    return await bff_fastapi.get_html(request)


@app.get("/get_ip_address")
async def get_ip_address():
    return f"{bff_fastapi.local_ip}:{bff_fastapi.port}"


@app.get("/get_input_templates")
async def get_input_templates():
    return await bff_fastapi.call_rpc("get_input_templates", {})


@app.post("/save_input_template")
async def save_input_template(request: Request):
    return await bff_fastapi.save_input_template(request)


@app.delete("/delete_input_template")
async def delete_input_template(request: Request):
    return await bff_fastapi.delete_input_template(request)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await bff_fastapi.websocket_endpoint(websocket)

if __name__ == '__main__':
    logger = Logger("Log", "BFF-FASTAPI_Server.log", True)
    bff_fastapi = BffFastAPI('192.168.0.13:5000')

    logging.info("+++++++++++++++++++++++++BFF-FASTAPI server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=bff_fastapi.local_ip, port=bff_fastapi.port, access_log=True)
    logging.info("-------------------------BFF-FASTAPI server was stopped-------------------------")
