"""
Author: [https://github.com/KirillShonkhorov/PIONER.git]
Date Created: [23.04.24]
Purpose: [All Pydantic data models used in the microservice.]
"""

import fastapi_jsonrpc as jsonrpc
from fastapi import Body
from pydantic import BaseModel


class Error(jsonrpc.BaseError):
    """Custom error class for server errors."""
    CODE = 5000
    MESSAGE = 'Server Error'

    class DataModel(BaseModel):
        details: str
        status_code: int


class IpAddressModel(BaseModel):
    ip: str
    port: int


class JsonRpcModel(BaseModel):
    jsonrpc: str
    id: str
    method: str
    params: dict


class InputTemplateModel(BaseModel):
    file_name: str = Body(..., examples=["template.txt"])
    file_content: str = Body(..., examples=["content"])


class InputParamsModel(BaseModel):
    in_file: InputTemplateModel
