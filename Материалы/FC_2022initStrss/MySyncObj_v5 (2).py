import sys
from typing import Union
import fastapi_jsonrpc as jsonrpc
from pydantic import BaseModel
from fastapi import Body
import requests
import json
import time
from enum import Enum
from contextlib import asynccontextmanager
from threading import Timer
import random

api_v1 = jsonrpc.Entrypoint('/api/v1/jsonrpc')

class State(Enum):
    LEADER = 1
    CANDIDATE = 2
    FOLLOWER = 3


class MyError(jsonrpc.BaseError):
    CODE = 5000
    MESSAGE = 'My error'

    class DataModel(BaseModel):
        details: str


class OwnOutDataModel(BaseModel):
    datas: float
    tag: str


class VoteInDataModel(BaseModel):
    term: float
    candidate_id: str


class VoteOutDataModel(BaseModel):
    term: float
    vote_granted: bool


class AppendInDataModel(BaseModel):
    term: float
    leader_id: str


class AppendOutDataModel(BaseModel):
    term: float
    success: bool


class OwnInDataModel(BaseModel):
    tag: str = Body(..., examples=["square"]),
    x: float = Body(..., examples=[0])


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class MySyncObj():
    loc_ip = "192.168.0.169"
    # loc_ip = "10.9.72.208"
    # loc_ip = "192.168.58.222"
    # loc_ip = "192.168.1.181"
    other_ports = []
    cur_state = State.FOLLOWER
    self_port = None
    other_port = None
    ip_port_for_rpc = None
    heartbeat = False
    cur_term = 0
    voted_for = None
    timestamp = None
    timer = None
    election_timeout = None

    def __init__(self):
        self.timer = RepeatTimer(5.0, self.do_work)
        pass

    def updTM(self):
        self.timestamp = time.time()

    def getTM(self):
        return self.timestamp

    def init_address(self, starting_p, self_p, amount):
        starting_p_int = int(starting_p)
        self.self_port = int(self_p)
        for i in range(int(amount)):
            if starting_p_int != int(self_p):
                self.other_ports.append(starting_p_int)
            starting_p_int += 1
        self.other_port = self.other_ports[0]

        self.ip_port_for_rpc = self.loc_ip + ":" + str(self.other_port)

    loc_index = 0

    def call_rpc(self, method: str, rpc_params: BaseModel, dest_port: str = None):
        if dest_port == None:
            dest_port = self.ip_port_for_rpc
        url = "http://" + dest_port + "/api/v1/jsonrpc"
        headers = {'content-type': 'application/json'}

        loc_json_rpc = {"jsonrpc": "2.0",
                        "id": "0",
                        "method": method,
                        "params": {'in_params': rpc_params.dict()}
                        }

        try:
            response = requests.post(url, data=json.dumps(loc_json_rpc), headers=headers, timeout=0.5)
        except Exception as err:
            print("No answer from " + dest_port)
            return {'datas': 'error connection'}

        if response.status_code == 200:
            response = response.json()

            if 'result' in response:
                return response['result']
            else:
                return {'datas': 'error fnc not found'}
        else:
            print('status code is not 200')
            return {'datas': 'error response'}

    def do_work(self):
        now = time.time()
        delay = now - self.timestamp
        print("Delay: " + str(int(delay / 60)) + " minutes; " + str(int(delay % 60)) + " seconds")
        if self.cur_state == State.LEADER:
            self.updTM()
            for port in self.other_ports:
                self.call_rpc("append_entries", AppendInDataModel(term=self.cur_term, leader_id=str(self.self_port)),
                              str(self.loc_ip) + ":" + str(port))
        elif self.cur_state == State.FOLLOWER:
            if delay > self.election_timeout and not self.heartbeat:
                self.cur_state = State.CANDIDATE
                self.election_timeout = 5 + (float(random.randint(10, 30)) * 0.01)
                self.election()
            elif self.heartbeat:
                self.heartbeat = False

    def election(self):
        self.cur_term += 1
        self.voted_for = self.self_port
        votes = 1
        for port in self.other_ports:
            response = self.call_rpc("request_vote",
                                     VoteInDataModel(term=self.cur_term, candidate_id=str(self.self_port)),
                                     str(self.loc_ip) + ":" + str(port))
            try:
                if int(response["term"]) > self.cur_term:
                    self.cur_state = State.FOLLOWER
                    return
                if bool(response["vote_granted"]):
                    votes += 1
            except Exception as err:
                continue
        if votes > (self.other_ports.__len__() / 2):
            self.cur_state = State.LEADER
            print("IM LEADER")
            for port in self.other_ports:
                 self.call_rpc("append_entries", AppendInDataModel(term=self.cur_term, leader_id=str(self.self_port)),
                               str(self.loc_ip) + ":" + str(port))
        self.election_timeout = float(random.randint(150, 300)) / 1000

    def request_vote_handler(self, in_params: VoteInDataModel) -> VoteOutDataModel:
        self.updTM()
        vote_granted = False
        print("Vote request from " + in_params.candidate_id + " to " + str(self.self_port))
        if self.cur_term <= in_params.term:
            vote_granted = True
            self.voted_for = in_params.candidate_id
            self.cur_term = in_params.term
            print("VOTED FOR " + " " + in_params.candidate_id)
        return VoteOutDataModel(term=self.cur_term, vote_granted=vote_granted)

    def append_entries_handler(self, in_params: AppendInDataModel) -> AppendOutDataModel:
        self.updTM()
        success = False
        print("Append request from " + in_params.leader_id + " to " + str(self.self_port))
        if self.cur_term <= in_params.term:
            self.cur_state = State.FOLLOWER
            success = True
            self.heartbeat = True
            self.cur_term = in_params.term
        return AppendOutDataModel(term=self.cur_term, success=success)

    def start(self):
        self.updTM()
        self.timer.start()
        self.election_timeout = 5 + (float(random.randint(10, 30)) * 0.01)


@api_v1.method(errors=[MyError])
def echo(
        in_params: OwnInDataModel
) -> OwnOutDataModel:
    global loc_index

    loc_params = in_params.dict()
    tag = loc_params['tag']
    x = loc_params['x']

    fnc_pow = lambda inp, p: inp ** p
    funcs = {"square": 2, "cubic": 3}
    if tag not in funcs:
        tag = 'error'

    if tag == 'error':
        raise MyError(data={'details': 'error'})
    else:
        loc_index = fnc_pow(x, funcs[tag])
        return OwnOutDataModel(datas=loc_index, tag=tag + " my port is " + str(my_raft.self_port))


@api_v1.method(errors=[MyError])
def request_vote(in_params: VoteInDataModel) -> VoteOutDataModel:
    return my_raft.request_vote_handler(in_params)


@api_v1.method(errors=[MyError])
def append_entries(in_params: AppendInDataModel) -> AppendOutDataModel:
    return my_raft.append_entries_handler(in_params)




if __name__ == '__main__':
    my_raft = MySyncObj()
    args = sys.argv[1:]
    my_raft.init_address(args[0], args[1], args[2])


    @asynccontextmanager
    async def lifespan(app: jsonrpc.API):
        my_raft.start()
        yield


    app = jsonrpc.API(lifespan=lifespan)

    app.bind_entrypoint(api_v1)
    app.add_api_route("/request_vote_rpc", get_vote, methods=["GET"])
    app.add_api_route("/echo_rpc", get_echo, methods=["GET"])

    import uvicorn

    uvicorn.run(app, host=my_raft.loc_ip, port=my_raft.self_port)
