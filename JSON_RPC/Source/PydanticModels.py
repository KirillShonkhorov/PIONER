"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [23.04.24]
Purpose: [All Pydantic data models used in the microservice.]
"""

import logging
import fastapi_jsonrpc as jsonrpc

from typing import List, Dict, Optional
from fastapi import Body
from pydantic import BaseModel


class Error(jsonrpc.BaseError):
    """Custom error class for server errors."""
    CODE = 5000
    MESSAGE = 'Server Error'

    class DataModel(BaseModel):
        details: str
        status_code: int


class FileParser(BaseModel):
    @classmethod
    def parse_file(cls, file_path: str, **kwargs) -> List['FileParser']:
        """
        Parsing files from a folder and return them.

        :exception: 508
        :return: List[parse files in folder]
        """

        logging.info(f"\t\t****Starting parse a '{file_path}' file****\t\t")

        data = []
        try:
            with open(file_path, 'r') as file:
                next(file)

                for line in file:
                    values = [float(val) for val in line.split()]
                    logging.debug(f"Values in line:\n{values}")
                    model_instance = cls(**dict(zip(cls.__annotations__, values)))
                    data.append(model_instance)

            return data

        except Exception as error508:
            logging.exception(f"JSON-RPC_Server error while parsing '{file_path}' file:\n{error508}")
            raise Error(data={'details': f"JSON-RPC_Server error while parsing '{file_path}' file:\n{error508}", 'status_code': 508})
        finally:
            logging.info(f"\t\t****Finish parse a '{file_path}' file****\t\t")


class Displacements(FileParser):
    node: int
    x: float
    y: float
    u: float
    v: float


class Stress(FileParser):
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


class Failure(FileParser):
    element: int
    int_point: int
    x: float
    y: float
    ind_failure: int
    maximal_principal_stress_direction: float


class PlotModel(BaseModel):
    script: str
    div: str


class GraphsModel(BaseModel):
    displacements: Dict[str, PlotModel]
    stress: Dict[str, PlotModel]


class ProcessOutputModel(BaseModel):
    displacements: Dict[str, List[Displacements]]
    stress: Dict[str, List[Stress]]
    stress_rotated: Dict[str, List[Stress]]
    failure: Dict[str, List[Failure]]
    graphs: Optional[GraphsModel] = None


class InputTemplateModel(BaseModel):
    file_name: str = Body(..., examples=["template.txt"])
    file_content: str = Body(..., examples=["content"])


class InputTemplateListModel(BaseModel):
    templates: List[InputTemplateModel]
