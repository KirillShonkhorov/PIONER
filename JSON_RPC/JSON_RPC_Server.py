import re
import shutil
import socket
import subprocess
import uvicorn

from Logger import *
from PydanticModels import *
from BokehWriter import BokehWriter

api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')


class JSONRPC:
    def __init__(self, local_ip='0.0.0.0', port=5000):
        self.local_ip = self.get_local_ip(local_ip)
        self.port = port

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

    async def delete_input_template(self, in_file: InFileModel):
        logging.info("****Start processing the 'delete_input_template' request****")

        file_path = f"InputTemplates/{in_file.fileName}"

        if await self.check_file(file_path, 400, "delete_input_template"):
            try:
                os.remove(file_path)
                logging.debug(f"The file '{file_path}' has been delete")
                return True

            except Exception as e:
                logging.exception(f"JSON-RPC_Server server error: {e}")
                raise Error(data={'details': f'JSON-RPC_Server server error: {e}', 'status_code': 507})
            finally:
                logging.info("****Finish processing the 'delete_input_template' request****")

    @staticmethod
    async def save_input_template(in_file: InputTemplateModel):
        logging.info("****Start processing the 'save_input_template' request****")

        file_path = f"InputTemplates/{in_file.fileName}"

        try:
            with open(file_path, "w") as file:
                file.write(in_file.fileContent)
            logging.debug(f"The file '{file_path}' has been create:\n'{in_file.fileContent}'")
            return None

        except Exception as e:
            logging.exception(f"JSON-RPC_Server server error: {e}")
            raise Error(data={'details': f'JSON-RPC_Server server error: {e}', 'status_code': 508})
        finally:
            logging.info("****Finish processing the 'save_input_template' request****")

    @staticmethod
    async def get_input_templates() -> Dict[str, str]:
        logging.info("****Start processing the 'get_input_templates' request****")

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
            logging.exception(f"JSON-RPC_Server server error: {e}")
            raise Error(data={'details': f'JSON-RPC_Server server error: {e}', 'status_code': 504})
        finally:
            logging.debug(f"Request 'get_input_templates' return next input templates:\n'{files_data}'")
            logging.info("****Finish processing the 'get_input_templates' request****")

    async def run_selected_template(self, in_file: InFileModel) -> ProcessOutputModel:
        logging.info("****Start processing the 'run_selected_template' request****")

        if await self.check_file(f"InputTemplates/{in_file.fileName}", 401, "run_selected_template"):
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
                logging.exception(f"JSON-RPC_Server server error: {e}")
                raise Error(data={'details': f'JSON-RPC_Server server error: {e}', 'status_code': 506})
            finally:
                logging.info("****Finish processing the 'run_selected_template' request****")

    async def run_pioner(self) -> ProcessOutputModel:
        logging.info("****Start processing the 'run_pioner' request****")

        if await self.check_file("input.txt", 500, "run_pioner"):
            try:
                await self.run_fc_2022initstrss()

                displacements_data = await self.process_files_in_folder('Displacements', Displacements)
                stress_data = await self.process_files_in_folder('Stress', Stress)
                stress_rotated_data = await self.process_files_in_folder('StressRotated', Stress)
                failure_data = await self.process_files_in_folder('Failure', Failure)

                result = ProcessOutputModel(
                    displacements=displacements_data,
                    stress=stress_data,
                    stress_rotated=stress_rotated_data,
                    failure=failure_data
                )

                result.graphs = await BokehWriter.create_plots(result)

                logging.debug(f"Request have ProcessOutputModel:\n{result}")
                return result

            except subprocess.CalledProcessError as e:
                logging.exception(f"Error while executing the process: {e}")
                raise Error(data={'details': f'Error while executing the process: {e}', 'status_code': 501})
            except Exception as e:
                logging.exception(f"JSON-RPC_Server server error: {e}")
                raise Error(data={'details': f'JSON-RPC_Server server error: {e}', 'status_code': 505})
            finally:
                logging.info("****Finish processing the 'run_pioner' request****")

    @staticmethod
    async def check_file(fileName, status_code, request):
        if not os.path.exists(fileName):
            logging.exception(f"The file '{fileName}' was not found. {status_code}")
            logging.info(f"****Finish processing the '{request}' request****")
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
                    logging.debug(f"{item_name} was deleted")
                except Exception as e:
                    logging.exception(f"Error while deleting '{item_name}'. Exception: {e}")
            else:
                logging.debug(f"{item_name} wasn't found")

    @staticmethod
    async def process_files_in_folder(folder: str, model_class: type) -> Dict[str, List[BaseModelWithFileParsing]]:
        logging.info(f"\t****Starting read a '{folder}' folder****\t")

        data = {}

        try:
            files = sorted(os.listdir(folder), key=lambda x: int(re.search(r'\d+', x).group()))

            logging.debug(f"Folder '{folder}' have a files:\n{files}")

            for file_number, filename in enumerate(files, start=1):
                if filename.startswith(f"{model_class.__name__}."):
                    file_path = os.path.join(folder, filename)
                    data[f"{model_class.__name__}.{file_number}"] = model_class.parse_file(file_path)

            logging.debug(f"Files in '{folder}' folder have a parse data:\n{data}")
            return data

        except Exception as error:
            logging.exception(f"JSON-RPC_Server server error while reading '{folder}' folder:\n{error}")
            raise Error(data={'details': f"JSON-RPC_Server server error while reading '{folder}' folder:\n{error}", 'status_code': 502})
        finally:
            logging.info(f"\t****'{folder}' was read****\t")


@api_v1.method(errors=[Error])
async def run_selected_template(in_file: InFileModel) -> ProcessOutputModel:
    return await json_rpc.run_selected_template(in_file)


@api_v1.method(errors=[Error])
async def run_pioner() -> ProcessOutputModel:
    return await json_rpc.run_pioner()


@api_v1.method(errors=[Error])
async def get_input_templates() -> Dict[str, str]:
    return await json_rpc.get_input_templates()


@api_v1.method(errors=[Error])
async def save_input_template(in_file: InputTemplateModel):
    return await json_rpc.save_input_template(in_file)


@api_v1.method(errors=[Error])
async def delete_input_template(in_file: InFileModel):
    return await json_rpc.delete_input_template(in_file)

if __name__ == '__main__':
    logger = Logger("Log", "JSON-RPC_Server.log", True)

    json_rpc_host = os.getenv('JSON_RPC_HOST', '0.0.0.0')
    json_rpc_port = os.getenv('JSON_RPC_PORT', 5000)

    json_rpc = JSONRPC(json_rpc_host, int(json_rpc_port))

    app = jsonrpc.API()
    app.bind_entrypoint(api_v1)

    logging.info("+++++++++++++++++++++++++JSON-RPC server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=json_rpc.local_ip, port=json_rpc.port, access_log=True)
    logging.info("-------------------------JSON-RPC server was stopped-------------------------")
