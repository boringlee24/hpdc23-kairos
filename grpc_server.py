import numpy as np
import os
import sys
import argparse
import time
import json 
from pathlib import Path
import signal
import grpc
from concurrent import futures
import random
import math
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if f'{str(ROOT)}/grpc' not in sys.path:
    sys.path.append(f'{str(ROOT)}/grpc')
import grpc_pb2, grpc_pb2_grpc

class Scheduler(grpc_pb2_grpc.SchedulerServicer):
    def __init__(self, args):
        super().__init__()
        self.model = args.model
        self.vm = args.vm
        # construct dict for latency lookup
        self.lat_dict = {}
        self.idx = args.port - 50051 # the gRPC servers start from port 50051
        for batch in range(10, 1001, 10):
            path = f'data/{args.vm}/{args.model}_{batch}_1.json'
            path_load = f'data/logs_load/{args.vm}/{args.model}_{batch}_1.json'
            with open(path, 'r') as f:
                lat_list = json.load(f)
            with open(path_load, 'r') as f_load:
                load_list = np.asarray(json.load(f_load))
            total_lat = lat_list + load_list
            filter_lat = np.delete(total_lat, total_lat.argmax())
            self.lat_dict[batch] = filter_lat

    def Serve(self, request, context):
        batch_size = math.ceil(request.batch/10)*10
        q_wait = request.q_wait
        latency = random.choice(self.lat_dict[batch_size])
        start = time.time()
        while True:
            if (time.time() - start)*1000 >= latency:
                break
        return grpc_pb2.ServerReply(exe_time=latency, idx=self.idx, q_wait=q_wait) # ms

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dummy grpc server config')
    parser.add_argument('--model', type=str, help='model name, choose from ncf, rm2, wnd, mtwnd, dien', default='rm2')
    parser.add_argument('--vm', type=str, help='vm name, choose from c5n.2xlarge, g4dn.xlarge, r5n.large, t3.xlarge', default='g4dn.xlarge')
    parser.add_argument('--port', type=int, help='port number', default=50051)
    args = parser.parse_args()

    grpc_ins = Scheduler(args)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    grpc_pb2_grpc.add_SchedulerServicer_to_server(grpc_ins, server)
    server.add_insecure_port(f'[::]:{args.port}')
    server.start()
    server.wait_for_termination() 
