import grpc
from pathlib import Path
import json 
import argparse
import sys
import logging
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if f'{str(ROOT)}/grpc' not in sys.path:
    sys.path.append(f'{str(ROOT)}/grpc')
import grpc_pb2, grpc_pb2_grpc
import time

def run(args):
    # NOTE(gRPC Python Team): .close() is possible on a channel and should be
    # used in circumstances in which the with statement does not fit the needs
    # of the code.
    with grpc.insecure_channel(f'{args.node}:{args.port}', options=(('grpc.enable_http_proxy', 0),)) as channel:
        stub = grpc_pb2_grpc.SchedulerStub(channel)
        response = stub.Serve(grpc_pb2.JobMessage(batch=args.batch))
        print(f"Request latency: {response.exe_time}")

def run_async(args):
    def handle_response(response):
        print(f"Request latency: {response.exe_time}, request idx: {response.idx}, q_wait: {response.q_wait}")
    channel = grpc.insecure_channel(f'{args.node}:{args.port}')
    stub = grpc_pb2_grpc.SchedulerStub(channel)
    response_future = stub.Serve.future(grpc_pb2.JobMessage(batch=args.batch,q_wait=args.q_wait))    
    response_future.add_done_callback(lambda future: handle_response(future.result()))
    print('sleeping')
    time.sleep(5)
    print('finished')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='dummy grpc server config')
    parser.add_argument('--node', type=str, help='node name', default='localhost')
    parser.add_argument('--port', type=int, help='port number', default=50051)
    parser.add_argument('--batch', type=int, help='batch size', default=108)
    parser.add_argument('--q_wait', type=float, help='q_wait time', default=0.5)
    args = parser.parse_args()

    logging.basicConfig()
    run_async(args)
    # run(args)