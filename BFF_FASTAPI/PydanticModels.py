import fastapi_jsonrpc as jsonrpc

from pydantic import BaseModel


class Error(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'Server Error'

    class DataModel(BaseModel):
        details: str
        status_code: int


class IpAddressModel(BaseModel):
    ip: str
    port: int
