import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from fastapi import Body

app = jsonrpc.API()
api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')

class Error(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'Unknown error'

    class DataModel(BaseModel):
        details: str


class inDataModel(BaseModel):
    tag: str = Body(..., examples=["square"]),
    x : float = Body(..., examples=[0])

class outDataModel(BaseModel):
    datas: float
    tag: str

@api_v1.method(errors=[Error])
async def echo(
    in_params : inDataModel
) -> outDataModel:

    loc_params = in_params.dict()
    tag = loc_params['tag']
    x = loc_params['x']

    fnc_pow = lambda inp, p : inp**p
    funcs = {"square" : 2, "cubic" : 3}
    if ( tag not in funcs):
        tag = 'error'

    if tag == 'error':
        raise Error(data={'details': 'error'})
    else:
        loc_index = fnc_pow(x, funcs[tag])
        return outDataModel(datas=loc_index, tag=tag)

app.bind_entrypoint(api_v1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('jrpc_fastapi:app', port=4000, access_log=False)