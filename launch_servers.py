# launches a series of dummy gRPC servers according to input

import subprocess
import json
import argparse
import socket

parser = argparse.ArgumentParser(description='dummy grpc server config')
parser.add_argument('--model', type=str, help='model name, choose from ncf, rm2, wnd, mtwnd, dien', default='rm2')
parser.add_argument('--port', type=int, help='port number', default=50051)
args = parser.parse_args()

port = args.port

with open('config.json') as f:
    config = json.load(f)

service_addr = [] # scheduler does not need to know which instance it is run on
proc_list = []
hostname = socket.gethostname()

for k, v in config.items():
    for i in range(v):
        # launch the grpc server
        cmd = f'python grpc_server.py --model {args.model} --vm {k} --port {port}'
        out_file = f'/scratch/li.baol/kairos_logs/{port}.out'
        err_file = f'/scratch/li.baol/kairos_logs/{port}.err'
        with open(out_file, 'w+') as out, open(err_file, 'w+') as err:
            proc = subprocess.Popen([cmd], shell=True, stdout=out, stderr=err)
        proc_list.append(proc)
        service_addr.append(f'{hostname}:{port}')
        port += 1

with open('service_addr.json', 'w') as f:
    json.dump(service_addr, f, indent=4)

exit_codes = [p.wait() for p in proc_list]
