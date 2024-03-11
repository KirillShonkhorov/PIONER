import json
import os
import re
import shutil
import logging
import subprocess
import uvicorn
import fastapi_jsonrpc as jsonrpc

from typing import List, Dict
from bokeh.layouts import gridplot
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure
from pydantic import BaseModel
from fastapi import Body
from Logger import Logger

api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')


class Error(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'JSON-RPC Server Error'

    class DataModel(BaseModel):
        details: str
        status_code: int


class BaseModelWithFileParsing(BaseModel):
    @classmethod
    def parse_file(cls, file_path: str, **kwargs) -> List['BaseModelWithFileParsing']:
        data = []

        with open(file_path, 'r') as file:
            next(file)  # Пропускаем заголовок

            for line in file:
                values = [float(val) if val.replace('.', '', 1).isdigit() else float(val) for val in line.split()]
                model_instance = cls(**dict(zip(cls.__annotations__, values)))
                data.append(model_instance)

        return data


class Displacements(BaseModelWithFileParsing):
    node: int
    x: float
    y: float
    u: float
    v: float


class Stress(BaseModelWithFileParsing):
    element: int
    int_point: int
    x: float
    y: float
    sigma_xx: float
    sigma_yy: float
    sigma_xy: float
    sigma_zz: float
    max_stress: float
    interm_stress: float
    min_stress: float
    time: float


class Failure(BaseModelWithFileParsing):
    element: int
    int_point: int
    x: float
    y: float
    ind_failure: int
    maximal_principal_stress_direction: float


class ProcessOutputModel(BaseModel):
    displacements: Dict[str, List[Displacements]]
    stress: Dict[str, List[Stress]]
    stress_rotated: Dict[str, List[Stress]]
    failure: Dict[str, List[Failure]]


class InputTemplateModel(BaseModel):
    fileName: str = Body(..., examples=["new_template.txt"])
    fileContent: str = Body(..., examples=["content"])


class InFileModel(BaseModel):
    fileName: str = Body(..., examples=["full_input.txt"])


class BokehWriter:
    @staticmethod
    async def create_displacements_plot(displacements_data: Dict[str, List[Displacements]]):
        plots = []
        for filename, displacements_list in displacements_data.items():

            # Swap third and fourth elements in 'x' and 'y'
            swapped_x = [d.x + d.u for d in displacements_list]
            swapped_y = [d.y + d.v for d in displacements_list]
            swapped_x[2], swapped_x[3] = swapped_x[3], swapped_x[2]
            swapped_y[2], swapped_y[3] = swapped_y[3], swapped_y[2]

            source = ColumnDataSource(data=dict(
                node=[d.node for d in displacements_list],
                # x=[d.x for d in displacements_list],
                # y=[d.y for d in displacements_list],
                x=swapped_x,
                y=swapped_y,
                u=[d.u for d in displacements_list],
                v=[d.v for d in displacements_list]
            ))

            print(f"Node {source.data.get('node')}. X {source.data.get('x')} Y {source.data.get('y')}")

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="blue", line_color="black")
            plots.append(p)

        # Do not save to file, instead, get components
        script, div = components(gridplot(plots, ncols=1))
        return script, div

    @staticmethod
    async def create_stress_plot(stress_data: Dict[str, List[Stress]]):
        plots = []
        for filename, stress_list in stress_data.items():

            # Swap third and fourth elements in 'x' and 'y'
            swapped_x = [d.x for d in stress_list]
            swapped_y = [d.y for d in stress_list]
            swapped_x[2], swapped_x[3] = swapped_x[3], swapped_x[2]
            swapped_y[2], swapped_y[3] = swapped_y[3], swapped_y[2]

            source = ColumnDataSource(data=dict(
                int_point=[d.int_point for d in stress_list],
                # x=[d.x for d in stress_list],
                # y=[d.y for d in stress_list],
                x=swapped_x,
                y=swapped_y
            ))

            print(f"Int point {source.data.get('int_point')}. X {source.data.get('x')} Y {source.data.get('y')}")

            p = figure(title=filename, x_axis_label='X-coordinate', y_axis_label='Y-coordinate')
            p.patch('x', 'y', source=source, fill_color="red", line_color="black")
            plots.append(p)

        # Do not save to file, instead, get components
        script, div = components(gridplot(plots, ncols=1))
        return script, div

    @classmethod
    async def create_plots(cls, result: ProcessOutputModel) -> str:
        displacements_scripts, displacements_divs = await cls.create_displacements_plot(result.displacements)
        stress_scripts, stress_divs = await cls.create_stress_plot(result.stress)

        # Удаляем теги <script> и <div> из полученных данных
        displacements_scripts = displacements_scripts[44:-15]
        displacements_divs = displacements_divs[5:-7]
        stress_scripts = stress_scripts[44:-15]
        stress_divs = stress_divs[5:-7]

        print(f"!{displacements_scripts}!")
        print(f"!{displacements_divs}!")
        print(f"!{stress_scripts}!")
        print(f"!{stress_divs}!")

        json_data = json.dumps({
            "displacements": {"scripts": displacements_scripts, "divs": displacements_divs},
            "stress": {"scripts": stress_scripts, "divs": stress_divs}
        })

        return json_data


class JSONRPC:
    def __init__(self, local_ip='localhost', port=5000):
        self.local_ip = local_ip
        self.port = port

    @staticmethod
    async def save_input_template(in_file: InputTemplateModel):
        logging.debug("****Start processing the 'save_input_template' request****")

        file_path = f"InputTemplates/{in_file.fileName}"

        try:
            with open(file_path, "w") as file:
                file.write(in_file.fileContent)
            logging.debug(f"The file '{file_path}' has been create:\n'{in_file.fileContent}'")
            return None

        except Exception as e:
            logging.exception(f"JSON-RPC server error: {e}")
            raise Error(data={'details': f'JSON-RPC server error: {e}', 'status_code': 505})
        finally:
            logging.debug("****Finish processing the 'save_input_template' request****")

    @staticmethod
    async def get_input_templates() -> Dict[str, str]:
        logging.debug("****Start processing the 'get_input_templates' request****")

        files_data = {}

        try:
            for filename in os.listdir("InputTemplates"):
                file_path = os.path.join("InputTemplates", filename)
                if os.path.isfile(file_path):
                    logging.debug(f"{file_path} is file")
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    logging.debug(f"The file '{file_path}' has been read:\n'{file_content}'")
                    files_data[f"{filename}"] = file_content

            return files_data

        except Exception as e:
            logging.exception(f"JSON-RPC server error: {e}")
            raise Error(data={'details': f'JSON-RPC server error: {e}', 'status_code': 504})
        finally:
            logging.debug(f"Request 'get_input_templates' return next input templates:\n'{files_data}'")
            logging.debug("****Finish processing the 'get_input_templates' request****")

    async def run_selected_template(self, in_file: InFileModel) -> str:
        logging.debug("****Start processing the 'run_selected_template' request****")

        if await self.check_file(f"InputTemplates/{in_file.fileName}", 400, "run_selected_template"):
            try:
                # Открываем файл и читаем его содержимое
                with open(f"InputTemplates/{in_file.fileName}", "r") as file:
                    content = file.read()
                logging.debug(f"The file 'InputTemplates/{in_file.fileName}' has been read:\n'{content}'")

                # Сохраняем полученный результат в файл "input.txt"
                with open("input.txt", "w") as output_file:
                    output_file.write(content)
                logging.debug(f"The file 'input.txt' has been create:\n'{content}'")

                return await self.run_pioner()

            except Exception as e:
                logging.exception(f"JSON-RPC server error: {e}")
                raise Error(data={'details': f'JSON-RPC server error: {e}', 'status_code': 503})
            finally:
                logging.debug("****Finish processing the 'run_selected_template' request****")

    async def run_pioner(self) -> str:
        logging.debug("****Start processing the 'run_pioner' request****")

        if await self.check_file("input.txt", 500, "run_pioner"):
            try:
                await self.run_fc_2022initstrss()

                displacements_data = await self.process_files_in_folder('Displacements', Displacements)
                logging.debug('Displacements was read')

                stress_data = await self.process_files_in_folder('Stress', Stress)
                logging.debug('Stress was read')

                stress_rotated_data = await self.process_files_in_folder('StressRotated', Stress)
                logging.debug('StressRotated was read')

                failure_data = await self.process_files_in_folder('Failure', Failure)
                logging.debug('Failure was read')

                result = ProcessOutputModel(
                    displacements=displacements_data,
                    stress=stress_data,
                    stress_rotated=stress_rotated_data,
                    failure=failure_data
                )

                logging.debug(f"Request have ProcessOutputModel:\n{result}")
                return await BokehWriter.create_plots(result)

            except subprocess.CalledProcessError as e:
                logging.error(f"Error while executing the process: {e}")
                raise Error(data={'details': f'Error while executing the process: {e}', 'status_code': 501})
            except Exception as e:
                logging.exception(f"JSON-RPC server error: {e}")
                raise Error(data={'details': f'JSON-RPC server error: {e}', 'status_code': 502})
            finally:
                logging.debug("****Finish processing the 'run_pioner' request****")

    @staticmethod
    async def check_file(fileName, status_code, request):
        if not os.path.exists(fileName):
            logging.error(f"The file '{fileName}' was not found. {status_code}")
            logging.debug(f"****Finish processing the '{request}' request****")
            raise Error(data={'details': f"The file '{fileName}' was not found", 'status_code': status_code})

        return True

    async def run_fc_2022initstrss(self):
        await self.remove_files_and_folders()

        logging.info('FC_2022initStrss.exe IS STARTED')
        subprocess.run(['FC_2022initStrss.exe'], check=True)
        logging.info('FC_2022initStrss.exe IS FINISHED')

    @staticmethod
    async def remove_files_and_folders():
        items_to_remove = [
            "iteration_statistic.txt",
            "echo_output.txt",
            "StressRotated",
            "Stress",
            "Patran",
            "Failure",
            "Displacements"
        ]

        for item_name in items_to_remove:
            if os.path.exists(item_name):
                try:
                    if os.path.isfile(item_name):
                        os.remove(item_name)
                    else:
                        shutil.rmtree(item_name)
                    logging.info(f"{item_name} was deleted")
                except Exception as e:
                    logging.error(f"Error while deleting '{item_name}'. Exception: {e}")
            else:
                logging.info(f"{item_name} wasn't found")

    @staticmethod
    async def process_files_in_folder(folder: str, model_class: type) -> Dict[str, List[BaseModelWithFileParsing]]:
        data = {}

        files = sorted(os.listdir(folder), key=lambda x: int(re.search(r'\d+', x).group()))

        for file_number, filename in enumerate(files, start=1):
            if filename.startswith(f"{model_class.__name__}."):
                file_path = os.path.join(folder, filename)
                data[f"{model_class.__name__}.{file_number}"] = model_class.parse_file(file_path)

        return data


@api_v1.method(errors=[Error])
async def run_selected_template(in_file: InFileModel) -> str:
    return await json_rpc.run_selected_template(in_file)


@api_v1.method(errors=[Error])
async def run_pioner() -> str:
    return await json_rpc.run_pioner()


@api_v1.method(errors=[Error])
async def get_input_templates() -> Dict[str, str]:
    return await json_rpc.get_input_templates()


@api_v1.method(errors=[Error])
async def save_input_template(in_file: InputTemplateModel):
    return await json_rpc.save_input_template(in_file)


if __name__ == '__main__':
    logger = Logger("Log", "JSON-RPC_Server.log")
    json_rpc = JSONRPC()

    app = jsonrpc.API()
    app.bind_entrypoint(api_v1)
    logging.debug("+++++++++++++++++++++++++JSON-RPC server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=json_rpc.local_ip, port=json_rpc.port, access_log=True)
    logging.debug("-------------------------JSON-RPC server was stopped-------------------------")
