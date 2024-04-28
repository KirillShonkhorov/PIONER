"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [25.04.24]
Purpose: [Backend from frontend (BFF) service for PIONER. Include API endpoints for working with it.]
"""

import io
import json
import socket
import httpx
import uvicorn

from pybase64 import b64decode

from fastapi import FastAPI, WebSocket, Request
from fastapi.websockets import WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from bokeh.models.widgets import FileInput
from bokeh.models import CustomJS, PreText
from bokeh.embed import components, json_item

from Logger import *
from PydanticModels import *
from WebsocketManager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()


class BffFastAPI:
    def __init__(self, rpc_server_ip='0.0.0.0', rpc_server_port=5000, local_ip='0.0.0.0', port=8000):
        """
        Initialize the BffFastAPI class with default IP and port values if they are not specified.
        :param rpc_server_ip: The local IP address to which the JSON-RPC server will bind. The default is "0.0.0.0".
        :param rpc_server_port: The port number to run the JSON-RPC server. Default is 5000.
        :param local_ip: The local IP address to which the server will be bound. The default is "0.0.0.0".
        :param port: The port number on which the server will be launched. Default is 8000.
        """
        self.local_ip = self.get_local_ip(local_ip)
        self.port = port
        self.rpc_server_url = f"http://{self.get_local_ip(rpc_server_ip)}:{rpc_server_port}/api/v1/jsonrpc/"
        self.templates = Jinja2Templates(directory="WebApplication/html")
        app.mount("/static", StaticFiles(directory="WebApplication"), name="static")
        logging.info(f"JSON-RPC server address: {self.rpc_server_url}")

    @staticmethod
    def get_local_ip(local_ip):
        """
        This method retrieves the local IP address. If a specific IP address is provided,
        it returns that address; otherwise, it tries to determine the local IP address
        using the socket library.
        :param local_ip: The local IP address provided.
        :return: The local IP address.
        """
        if local_ip == '0.0.0.0':
            try:
                ip_address = socket.gethostbyname(socket.gethostname())
                return ip_address
            except socket.gaierror:
                return local_ip
        else:
            return local_ip

    async def get_html(self, request: Request):
        """
        This method is responsible for processing the 'get_html' request, which involves rendering an HTML template.
        :exception: 500
        :param request: The HTTP request object.
        :return: A TemplateResponse object containing the rendered HTML template.
        """
        logging.info("****Start processing the 'get_html' request****")
        try:
            return self.templates.TemplateResponse("selectTemplate.html", {"request": request})
        except Exception as error500:
            logging.exception(f"BFF-FASTAPI_Server error: {error500}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error500}", 'status_code': 500})
        finally:
            logging.info("****Finish processing the 'get_html' request****")

    async def call_rpc(self, method, in_params):
        """
        This method is responsible for making an RPC call to a specified method with given input parameters.
        :exception: 400
        :exception: 501
        :param method: The name of the RPC method to call.
        :param in_params: Input parameters for the RPC method.
        :return: The result of the RPC call.
        """
        logging.info(f"****Start processing the 'call_rpc' request.****\n"
                     f"Method: '{method}'\nInput Params: '{in_params}'\n")

        url = f"{self.rpc_server_url}{method}"
        headers = {'content-type': 'application/json'}
        json_rpc = JsonRpcModel(jsonrpc="2.0", id="0", method=method, params=in_params)
        try:
            response = httpx.post(url, json=json_rpc.dict(), headers=headers, timeout=None)
            response.raise_for_status()
            response_data = response.json()
            logging.debug(f'Response for RPC was completed')

            if 'result' in response_data:
                logging.debug(f"RPC response have a result:\n'{response_data['result']}'")
                return response_data['result']
            else:
                logging.warning("RPC response haven't a result!")
                return Error(data={'details': f"BFF-FASTAPI_Server error: {response_data}. RPC response haven't a result.", 'status_code': 400})

        except Exception as error501:
            logging.exception(f'BFF-FASTAPI_Server error. RPC connection exception: {error501}')
            return Error(data={'details': f"BFF-FASTAPI_Server error. RPC connection exception: {error501}", 'status_code': 501})
        finally:
            logging.info(f"****Finish processing the 'call_rpc' request.****\n"
                         f"Method: '{method}'\nInput Params: '{in_params}'\n")

    async def light_app(self):
        """
        This method generates and returns HTML content.
        :exception: 502
        :return: An HTMLResponse object containing the generated HTML content
        """
        logging.info("****Start processing the 'light_app' request****")
        try:
            file_input = FileInput()
            file_input.js_on_change('filename', await self.create_custom_js_callback(file_input))

            generated_script, generated_div = components(file_input)

            return HTMLResponse(await self.generate_template(generated_script, generated_div))

        except Exception as error502:
            logging.exception(f"BFF-FASTAPI_Server error: {error502}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error502}", 'status_code': 502})
        finally:
            logging.info("****Finish processing the 'light_app' request****")

    @staticmethod
    async def create_custom_js_callback(file_input):
        """
        This method generates a custom JavaScript callback function that interacts with a FileInput object.
        :exception: 503
        :return: A CustomJS object representing the custom JavaScript callback
        """
        logging.info("****Start processing the 'create_custom_js_callback' request****")
        try:
            return CustomJS(args=dict(file_input=file_input), code="""
                    const fileName = file_input.filename;
                    const fileContent = file_input.value;

                    async function put_file(){
                        return await fetch('/create_content', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ fileName, fileContent })
                        }).then((response) => response.json())
                    }

                    const printFile = async () => {
                        const file = await put_file();
                        var div = document.getElementById('templates-container');
                        while(div.firstChild){
                            div.removeChild(div.firstChild);
                        }
                        Bokeh.embed.embed_item(file);
                    };

                    printFile();
                """)
        except Exception as error503:
            logging.exception(f"BFF-FASTAPI_Server error: {error503}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error503}", 'status_code': 503})
        finally:
            logging.info("****Finish processing the 'create_custom_js_callback' request****")

    @staticmethod
    async def generate_template(generated_script, generated_div):
        """
        This method generates HTML from a ready template and returns the updated content.
        :exception: 504
        :return: HTML
        """
        logging.info("****Start processing the 'generate_template' request****")
        try:
            with open("WebApplication/html/onePageApp.html", "r", encoding="utf-8") as file:
                html_content = file.read()

            html_content = html_content.replace("<!-- INSERT_SCRIPTS_HERE -->", generated_script)
            html_content = html_content.replace("<!-- INSERT_DIVS_HERE -->", generated_div)

            return html_content

        except Exception as error504:
            logging.exception(f"BFF-FASTAPI_Server error: {error504}")
            return Error(data={'details': f"BFF-FASTAPI_Server server error: {error504}", 'status_code': 504})
        finally:
            logging.info("****Finish processing the 'generate_template' request****")

    async def create_content(self, input_content):
        """
        This method generates the page content and returns the content.
        :exception: 505
        :return: update HTML
        """
        print(input_content)
        logging.info("****Start processing the 'create_content' request****")
        try:
            file_content = await self.decode_data(input_content['fileContent'])
            new_content = PreText(text=file_content)

            return json.dumps(json_item(new_content, "templates-container"))

        except Exception as error505:
            logging.exception(f"BFF-FASTAPI_Server error: {error505}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error505}", 'status_code': 505})
        finally:
            logging.info("****Finish processing the 'create_content' request****")

    @staticmethod
    async def decode_data(input_data):
        """
        Decode input Base64-encoded data.
        :exception: 506
        :return: Decoded text data.
        """
        logging.info("****Start processing the 'decode_data' request****")
        try:
            decoded = b64decode(input_data)
            f = io.BytesIO(decoded)
            text_obj = io.TextIOWrapper(f, encoding='utf-8')
            output_data = text_obj.read()

            return output_data

        except Exception as error506:
            logging.exception(f"BFF-FASTAPI_Server error: {error506}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error506}", 'status_code': 506})
        finally:
            logging.info("****Finish processing the 'decode_data' request****")

    async def delete_input_template(self, request: Request):
        """
        This method delete input template by file name.
        :exception: 507
        :return: None = success
        """
        logging.info("****Start processing the 'delete_input_template' request****")
        try:
            data = await request.json()
            file_name = data.get("fileName")

            in_params = InputParamsModel(in_file=InputTemplateModel(file_name=file_name, file_content=""))

            if await self.call_rpc("delete_input_template", in_params.dict()):
                logging.debug("Request return: True")
                return None

        except Exception as error507:
            logging.exception(f"BFF-FASTAPI_Server error: {error507}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error507}", 'status_code': 507})
        finally:
            logging.info("****Finish processing the 'delete_input_template' request****")

    async def save_input_template(self, request: Request):
        """
        This method save input template in system.
        :exception: 508
        :return: None = success
        """
        logging.info("****Start processing the 'save_input_template' request****")
        try:
            data = await request.json()
            file_name = data.get("fileName")
            file_content = data.get("fileContent")

            in_params = InputParamsModel(in_file=InputTemplateModel(file_name=file_name, file_content=file_content))

            result = await self.call_rpc("save_input_template", in_params.dict())
            logging.debug(f"Request return: {result}")
            return None

        except Exception as error508:
            logging.exception(f"BFF-FASTAPI_Server error: {error508}")
            return Error(data={'details': f"BFF-FASTAPI_Server error: {error508}", 'status_code': 508})
        finally:
            logging.info("****Finish processing the 'save_input_template' request****")

    async def websocket_endpoint(self, websocket: WebSocket):
        """
        This method allows you to work with a websocket connection.
        :exception: 508
        :return: None = success
        """
        logging.info("****Start processing the 'websocket_endpoint' request****")
        try:
            await manager.connect(websocket)
        except Exception as connect_error:
            await manager.disconnect(websocket)
            logging.exception(f"WebSocket was disconnected. Exception: {connect_error}")

        try:
            while True:
                data = await websocket.receive_text()
                logging.debug(f"Received data from WebSocket: {data}")

                in_params = InputParamsModel(in_file=InputTemplateModel(file_name=data, file_content=""))
                rpc_data = await self.call_rpc("run_selected_template", in_params.dict())
                await websocket.send_text(json.dumps(rpc_data))

        except WebSocketDisconnect:
            await manager.disconnect(websocket)
            logging.exception("The client has disconnected. Cleaned up")
        except Exception as websocket_error:
            logging.exception(f"WebSocket Exception: {websocket_error}")
        finally:
            logging.info("****Finish processing the 'websocket_endpoint' request****")


@app.get("/")
async def get_html(request: Request):
    return await bff_fastapi.get_html(request)


@app.get("/get_input_templates")
async def get_input_templates():
    return await bff_fastapi.call_rpc("get_input_templates", {})


@app.get("/light_app", response_class=HTMLResponse)
async def light_app():
    return await bff_fastapi.light_app()


@app.post("/create_content", response_class=HTMLResponse)
async def create_content(input_content: dict[str, str]):
    return await bff_fastapi.create_content(input_content)


@app.delete("/delete_input_template")
async def delete_input_template(request: Request):
    return await bff_fastapi.delete_input_template(request)


@app.post("/save_input_template")
async def save_input_template(request: Request):
    return await bff_fastapi.save_input_template(request)


@app.get("/get_ip_address")
async def get_ip_address() -> IpAddressModel:
    return IpAddressModel(ip=bff_fastapi.local_ip, port=str(bff_fastapi.port))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await bff_fastapi.websocket_endpoint(websocket)


if __name__ == '__main__':
    logger = Logger("Log", "BFF-FASTAPI_Server.log", True)

    json_rpc_host = os.getenv('JSON_RPC_HOST', '0.0.0.0')
    json_rpc_port = os.getenv('JSON_RPC_PORT', 5000)

    bff_fastapi_host = os.getenv('BFF_FASTAPI_HOST', '0.0.0.0')
    bff_fastapi_port = os.getenv('BFF_FASTAPI_PORT', 8000)

    logging.info("+++++++++++++++++++++++++BFF-FASTAPI_Server was started+++++++++++++++++++++++++")

    bff_fastapi = BffFastAPI(json_rpc_host, int(json_rpc_port), bff_fastapi_host, int(bff_fastapi_port))

    uvicorn.run(app, host=bff_fastapi.local_ip, port=bff_fastapi.port, access_log=True)
    logging.info("-------------------------BFF-FASTAPI_Server was stopped-------------------------")
