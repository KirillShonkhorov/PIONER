"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [23.04.24]
Purpose: [Remote procedure call (RPC) service for PIONER. Include API endpoints for working with it.]
"""

import re
import shutil
import socket
import subprocess
import uvicorn

from fastapi.responses import RedirectResponse

from Logger import *
from PydanticModels import *
from BokehWriter import BokehWriter

api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')


class JSONRPC:
    def __init__(self, local_ip='0.0.0.0', port=5000):
        """
        Initialize JSONRPC class with default IP and port values if not provided.
        :param local_ip: The local IP address to bind the server to. Default is '0.0.0.0'.
        :param port: The port number to run the server on. Default is 5000.
        """
        self.local_ip = self.get_local_ip(local_ip)
        self.port = port

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

    @staticmethod
    async def get_input_templates() -> InputTemplateListModel:
        """
        Retrieve a list of InputTemplateModel objects.
        This method is used to obtain data from all existing templates.
        :exception: 500
        :return: InputTemplateListModel object containing a list of InputTemplateModel objects.
        """
        logging.info("****Start processing the 'get_input_templates' request****")

        templates_list = InputTemplateListModel(templates=[])
        try:
            for file_name in os.listdir("InputTemplates"):
                file_path = os.path.join("InputTemplates", file_name)
                if os.path.isfile(file_path):
                    logging.debug(f"{file_path} is file")
                    with open(file_path, 'r') as file:
                        file_content = file.read()
                    logging.debug(f"The file '{file_path}' has been read:\n'{file_content}'")
                    templates_list.templates.append(InputTemplateModel(file_name=file_name, file_content=file_content))

            return templates_list

        except Exception as error500:
            logging.exception(f"JSON-RPC_Server error: {error500}")
            raise Error(data={'details': f'JSON-RPC_Server error: {error500}', 'status_code': 500})
        finally:
            logging.debug(f"Request 'get_input_templates' return next input templates:\n'{templates_list}'")
            logging.info("****Finish processing the 'get_input_templates' request****")

    async def delete_input_template(self, in_file: InputTemplateModel):
        """
        Delete the specified input template file.
        :exception: 501
        :exception: 400
        :param in_file: The InputTemplateModel object representing the file to be deleted.
        """
        logging.info("****Start processing the 'delete_input_template' request****")

        file_path = f"InputTemplates/{in_file.file_name}"

        if await self.check_file(file_path, 400, "delete_input_template"):
            try:
                os.remove(file_path)
                logging.debug(f"The file '{file_path}' has been delete")
                return None

            except Exception as error501:
                logging.exception(f"JSON-RPC_Server error: {error501}")
                raise Error(data={'details': f'JSON-RPC_Server error: {error501}', 'status_code': 501})
            finally:
                logging.info("****Finish processing the 'delete_input_template' request****")

    @staticmethod
    async def check_file(file_name, status_code, request):
        """
        Check if the specified file exists.
        :param file_name: The name of the file to check.
        :param status_code: The status code to raise if the file does not exist.
        :param request: The name of the request being processed.
        :return: True if the file exists, otherwise raise an Error.
        """
        if not os.path.exists(file_name):
            logging.exception(f"The file '{file_name}' was not found. {status_code}")
            logging.info(f"****Finish processing the '{request}' request****")
            raise Error(data={'details': f"The file '{file_name}' was not found", 'status_code': status_code})

        return True

    @staticmethod
    async def save_input_template(in_file: InputTemplateModel):
        """
        Save the input template file.
        :exception: 502
        :param in_file: The InputTemplateModel object representing the file to be saved.
        """
        logging.info("****Start processing the 'save_input_template' request****")

        file_path = f"InputTemplates/{in_file.file_name}"
        try:
            with open(file_path, "w") as file:
                file.write(in_file.file_content)
            logging.debug(f"The file '{file_path}' has been create:\n'{in_file.file_content}'")
            return None

        except Exception as error502:
            logging.exception(f"JSON-RPC_Server error: {error502}")
            raise Error(data={'details': f'JSON-RPC_Server error: {error502}', 'status_code': 502})
        finally:
            logging.info("****Finish processing the 'save_input_template' request****")

    async def run_selected_template(self, in_file: InputTemplateModel) -> ProcessOutputModel:
        """
        Run the selected template.
        :exception: 401
        :exception: 503
        :param in_file: The InputTemplateModel object representing the selected template file.
        :return: The ProcessOutputModel object containing the result of running the template.
        """
        logging.info("****Start processing the 'run_selected_template' request****")

        if await self.check_file(f"InputTemplates/{in_file.file_name}", 401, "run_selected_template"):
            try:
                with open(f"InputTemplates/{in_file.file_name}", "r") as file:
                    content = file.read()
                logging.debug(f"The file 'InputTemplates/{in_file.file_name}' has been read:\n'{content}'")

                with open("input.txt", "w") as output_file:
                    output_file.write(content)
                logging.debug(f"The file 'input.txt' has been create:\n'{content}'")

                return await self.run_pioner()

            except Exception as error503:
                logging.exception(f"JSON-RPC_Server error: {error503}")
                raise Error(data={'details': f'JSON-RPC_Server error: {error503}', 'status_code': 503})
            finally:
                logging.info("****Finish processing the 'run_selected_template' request****")

    async def run_pioner(self) -> ProcessOutputModel:
        """
        Run PIONER application.
        :exception: 504
        :exception: 505
        :exception: 506
        :return: The ProcessOutputModel object containing the result of running the application.
        """
        logging.info("****Start processing the 'run_pioner' request****")

        if await self.check_file("input.txt", 504, "run_pioner"):
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

            except subprocess.CalledProcessError as error505:
                logging.exception(f"Error while executing the process: {error505}")
                raise Error(data={'details': f'Error while executing the process: {error505}', 'status_code': 505})
            except Exception as error506:
                logging.exception(f"JSON-RPC_Server error: {error506}")
                raise Error(data={'details': f'JSON-RPC_Server error: {error506}', 'status_code': 506})
            finally:
                logging.info("****Finish processing the 'run_pioner' request****")

    @staticmethod
    async def process_files_in_folder(folder: str, model_class: type) -> Dict[str, List[FileParser]]:
        """
        Reading files from a folder and parsing them.
        :exception: 507
        :return: Dict {folder name: List[files in folder]}
        """
        logging.info(f"\t****Starting read a '{folder}' folder****\t")

        data = {}
        try:
            files = sorted(os.listdir(folder), key=lambda x: int(re.search(r'\d+', x).group()))

            logging.debug(f"Folder '{folder}' have a files:\n{files}")

            for file_number, file_name in enumerate(files, start=1):
                if file_name.startswith(f"{model_class.__name__}."):
                    file_path = os.path.join(folder, file_name)
                    data[f"{model_class.__name__}.{file_number}"] = model_class.parse_file(file_path)

            logging.debug(f"Files in '{folder}' folder have a parse data:\n{data}")
            return data

        except Exception as error507:
            logging.exception(f"JSON-RPC_Server error while reading '{folder}' folder:\n{error507}")
            raise Error(data={'details': f"JSON-RPC_Server error while reading '{folder}' folder:\n{error507}", 'status_code': 507})
        finally:
            logging.info(f"\t****'{folder}' was read****\t")

    async def run_fc_2022initstrss(self):
        """
        This method starts the FC_2022initStrss.exe process, which initializes
        the output files.
        :raises: subprocess.CalledProcessError: If the process execution fails.
        """
        await self.remove_files_and_folders()

        logging.info('FC_2022initStrss.exe IS STARTED')
        subprocess.run(['FC_2022initStrss.exe'], check=True)
        logging.info('FC_2022initStrss.exe IS FINISHED')

    @staticmethod
    async def remove_files_and_folders():
        """
        This method removes the files and folders specified in the items_to_remove list.
        :raises: Exception: If an error occurs while deleting files or folders.
        """

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
                except Exception as error:
                    logging.exception(f"Error while deleting '{item_name}'. Exception: {error}")
            else:
                logging.debug(f"{item_name} wasn't found")


@api_v1.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


@api_v1.method(errors=[Error])
async def get_input_templates() -> InputTemplateListModel:
    return await json_rpc.get_input_templates()


@api_v1.method(errors=[Error])
async def delete_input_template(in_file: InputTemplateModel):
    return await json_rpc.delete_input_template(in_file)


@api_v1.method(errors=[Error])
async def save_input_template(in_file: InputTemplateModel):
    return await json_rpc.save_input_template(in_file)


@api_v1.method(errors=[Error])
async def run_selected_template(in_file: InputTemplateModel) -> ProcessOutputModel:
    return await json_rpc.run_selected_template(in_file)


@api_v1.method(errors=[Error])
async def run_pioner() -> ProcessOutputModel:
    return await json_rpc.run_pioner()


if __name__ == '__main__':
    logger = Logger("Log", "JSON-RPC_Server.log", True)

    json_rpc_host = os.getenv('JSON_RPC_HOST', '0.0.0.0')
    json_rpc_port = os.getenv('JSON_RPC_PORT', 5000)

    json_rpc = JSONRPC(json_rpc_host, int(json_rpc_port))

    app = jsonrpc.API()
    app.bind_entrypoint(api_v1)

    logging.info("+++++++++++++++++++++++++JSON-RPC_Server was started+++++++++++++++++++++++++")
    uvicorn.run(app, host=json_rpc.local_ip, port=json_rpc.port, access_log=True)
    logging.info("-------------------------JSON-RPC_Server was stopped-------------------------")
