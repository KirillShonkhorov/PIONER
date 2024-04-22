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
        self.local_ip = self.get_local_ip(local_ip)
        self.port = port
        self.rpc_server_url = f"http://{self.get_local_ip(rpc_server_ip)}:{rpc_server_port}/api/v1/jsonrpc/"
        self.templates = Jinja2Templates(directory="WebApplication/html")
        app.mount("/static", StaticFiles(directory="WebApplication"), name="static")
        logging.info(f"JSON-RPC server address: {self.rpc_server_url}")

    @staticmethod
    def get_local_ip(local_ip):
        if local_ip == '0.0.0.0':
            try:
                ip_address = socket.gethostbyname(socket.gethostname())
                return ip_address
            except socket.gaierror:
                return local_ip  # Если не удается определить IP-адрес, вернуть исходное значение '0.0.0.0'
        else:
            return local_ip  # Если указан явный IP-адрес, вернуть его

    async def get_html(self, request: Request):
        try:
            logging.info("****Start processing the 'get_html' request****")
            return self.templates.TemplateResponse("selectTemplate.html", {"request": request})
        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 500})
        finally:
            logging.info("****Finish processing the 'get_html' request****")

    async def light_app(self):
        try:
            logging.info("****Start processing the 'light_app' request****")

            file_input = FileInput()
            file_input.js_on_change('filename', await self.create_custom_js_callback(file_input))

            script, div = components(file_input)

            return HTMLResponse(await self.generate_template(script, div))

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 507})
        finally:
            logging.info("****Finish processing the 'light_app' request****")

    async def create_content(self, input_content):
        try:
            logging.info("****Start processing the 'create_content' request****")

            file_content = await self.decode_data(input_content['fileContent'])
            new_content = PreText(text=file_content)

            return json.dumps(json_item(new_content, "templates-container"))

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 508})
        finally:
            logging.info("****Finish processing the 'create_content' request****")

    @staticmethod
    async def decode_data(input_data):
        try:
            logging.info("****Start processing the 'decode_data' request****")

            decoded = b64decode(input_data)
            f = io.BytesIO(decoded)
            text_obj = io.TextIOWrapper(f, encoding='utf-8')
            output_data = text_obj.read()

            return output_data

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 509})
        finally:
            logging.info("****Finish processing the 'decode_data' request****")

    @staticmethod
    async def create_custom_js_callback(file_input):
        try:
            logging.info("****Start processing the 'create_custom_js_callback' request****")

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

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 506})
        finally:
            logging.info("****Finish processing the 'create_custom_js_callback' request****")

    @staticmethod
    async def generate_template(gscripts, gdivs):
        try:
            logging.info("****Start processing the 'generate_template' request****")

            return f"""
                <!DOCTYPE html>
                <html lang="en">
                
                <head>
                    <meta charset="UTF-8">
                    <meta http-equiv="X-UA-Compatible" content="IE=edge">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>PIONER</title>
                
                    <link rel="stylesheet" href="/static/css/styles.css">
                </head>
                
                <body>
                    <header>
                        <h1>Добро пожаловать в "PIONER"</h1>
                        <nav>
                            <ul>
                                <li><a href="/">Главная</a></li>
                                <li><a href="#">Информация</a></li>
                                <li><a href="#">Контакты</a></li>
                            </ul>
                        </nav>
                    </header>
                
                    <main>
                        <section>
                            <div id="error-container" class="notification">
                                <h1 id="notification-msg"></h1>
                            </div>
                
                            <div><h2>Страница выбора шаблона входного файла</h2></div>
                
                            <div class="container">
                                <h3 id="container-title">Выберите шаблон</h3>
                                
                                {gdivs}
                                <div id="templates-container"></div>
                            </div>
                        </section>
                    </main>
                
                    <footer>
                        <p>&copy; 2024 Институт гидродинамики им. М.А. Лаврентьева СО РАН. Все права защищены.</p>
                    </footer>
                    
                    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-3.4.0.min.js"></script>
                    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-widgets-3.4.0.min.js"></script>
                    <script type="text/javascript" src="https://cdn.bokeh.org/bokeh/release/bokeh-tables-3.4.0.min.js"></script>
                    {gscripts}                
                </body>
                
                </html>
                """

        except Exception as error:
            logging.exception(f"BFF-FASTAPI server error: {error}")
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 504})
        finally:
            logging.info("****Finish processing the 'generate_template' request****")

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
                return None

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
            return Error(data={'details': f"BFF-FASTAPI server error: {error}", 'status_code': 505})
        finally:
            logging.info("****Finish processing the 'save_input_template' request****")

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
            logging.info(
                f"****Start processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'\n")

            url = f"{self.rpc_server_url}{method}"

            headers = {'content-type': 'application/json'}
            loc_json_rpc = {
                "jsonrpc": "2.0",
                "id": "0",
                "method": method,
                "params": in_params
            }

            response = httpx.post(url, json=loc_json_rpc, headers=headers, timeout=None)
            response.raise_for_status()
            response_data = response.json()
            logging.debug(f'Response for RPC was completed')

            if 'result' in response_data:
                logging.debug(f"RPC response have a result:\n'{response_data['result']}'")
                return response_data['result']
            else:
                logging.warning("RPC response haven't a result!")
                return Error(data={'details': f"RPC response haven't a result. Response description: {response_data}",
                                   'status_code': 400})

        except Exception as error:
            logging.exception(f'BFF-FASTAPI server error. RPC connection exception: {error}')
            return Error(
                data={'details': f"BFF-FASTAPI server error. RPC connection exception: {error}", 'status_code': 501})
        finally:
            logging.info(
                f"****Finish processing the 'call_rpc' request.****\nMethod: '{method}'\nInput Params: '{in_params}'\n")


@app.get("/")
async def get_html(request: Request):
    return await bff_fastapi.get_html(request)


@app.get("/get_ip_address")
async def get_ip_address() -> IpAddressModel:
    return IpAddressModel(ip=bff_fastapi.local_ip, port=str(bff_fastapi.port))


@app.get("/light_app", response_class=HTMLResponse)
async def light_app():
    return await bff_fastapi.light_app()


@app.post("/create_content", response_class=HTMLResponse)
async def create_content(input_content: dict[str, str]):
    return await bff_fastapi.create_content(input_content)


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

    json_rpc_host = '0.0.0.0'
    json_rpc_port = os.getenv('JSON_RPC_PORT', 5000)

    try:
        json_rpc_host = socket.gethostbyname('json_rpc')
    except Exception as error:
        logging.exception(f"BFF-FASTAPI server error. Environment for RPC doesn't not exist: {error}")

    bff_fastapi_host = os.getenv('BFF_FASTAPI_HOST', '0.0.0.0')
    bff_fastapi_port = os.getenv('BFF_FASTAPI_PORT', 8000)

    bff_fastapi = BffFastAPI(json_rpc_host, int(json_rpc_port), bff_fastapi_host, int(bff_fastapi_port))

    logging.info("+++++++++++++++++++++++++BFF-FASTAPI server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=bff_fastapi.local_ip, port=bff_fastapi.port, access_log=True)
    logging.info("-------------------------BFF-FASTAPI server was stopped-------------------------")
