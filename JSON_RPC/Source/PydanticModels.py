import logging
import fastapi_jsonrpc as jsonrpc

from typing import List, Dict, Optional
from fastapi import Body
from pydantic import BaseModel


class Error(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'Server Error'

    class DataModel(BaseModel):
        details: str
        status_code: int


class BaseModelWithFileParsing(BaseModel):
    @classmethod
    def parse_file(cls, file_path: str, **kwargs) -> List['BaseModelWithFileParsing']:
        logging.info(f"\t\t****Starting parse a '{file_path}' file****\t\t")

        data = []

        try:
            with open(file_path, 'r') as file:
                next(file)  # Пропускаем заголовок

                for line in file:
                    values = [float(val) for val in line.split()]
                    logging.debug(f"Values in line:\n{values}")
                    model_instance = cls(**dict(zip(cls.__annotations__, values)))
                    data.append(model_instance)

            return data

        except Exception as error:
            logging.exception(f"JSON-RPC server error while parsing '{file_path}' file:\n{error}")
            raise Error(data={'details': f"JSON-RPC server error while parsing '{file_path}' file:\n{error}", 'status_code': 503})
        finally:
            logging.info(f"\t\t****Finish parse a '{file_path}' file****\t\t")


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
    graphs: Optional[Dict[str, Dict[str, Dict[str, str]]]] = None


class InputTemplateModel(BaseModel):
    fileName: str = Body(..., examples=["new_template.txt"])
    fileContent: str = Body(..., examples=["content"])


class InFileModel(BaseModel):
    fileName: str = Body(..., examples=["input.txt"])
