import numpy as np
import json
import os
from pathlib import Path
import argparse
from itertools import product
from joblib import Parallel, delayed

class Results: # used to store results
    def __init__(self, key, cost, ub): 
        self.key = key
        self.cost = cost
        self.ub = ub # upperbound

parser = argparse.ArgumentParser(description='kairos query distributor')
parser.add_argument('--model', type=str, help='model name, choose from ncf, rm2, wnd, mtwnd, dien', default='rm2')
args = parser.parse_args()

with open(f'instance.json') as f:
    config = json.load(f)
cpus = config['ins_types'][1:]
init_cpu = 'r5n.large' # greedily choose the highest qps-to-cost ratio instance type
gpu = config['ins_types'][0]
max_num = config['max_num']

with open(f'allocator_profile.json') as f:
    profiles = json.load(f)[args.model]
gpu_qps = profiles[gpu]['qps']

def inner_loop(num1, num2, num3, num4):
    key = f'{num1}, {num2}, {num3}, {num4}'
    # returns upper bound of QPS
    total_price = sum(np.multiply(config['price'],[num1,num2,num3,num4]))
    if total_price > config['cost'] or num1 == 0:
        return
    elif num2 == 0 and num3 == 0 and num4 == 0:
        return Results(key, total_price, gpu_qps * num1)
    # calculate upperbound
    cpu_cnt = {cpus[0]:num2, cpus[1]:num3, cpus[2]:num4}
    cpu_qps = []
    cpu_small = []
    gpu_time = []
    cpu_batch = []
    for cpu, cnt in cpu_cnt.items():
        if cnt != 0:
#                cpu_qps.append(cnt * profiles[cpu].qps)
            cpu_batch.append(profiles[cpu]['vio_batch']) # violation batch size
            cpu_small.append(profiles[cpu]['small_ratio'])
            gpu_time.append(profiles[cpu]['time_ratio'])
    agg_batch = max(cpu_batch)
    agg_small = max(cpu_small)
    agg_time = max(gpu_time)
    for cpu, cnt in cpu_cnt.items():
        if cnt != 0:
            cpu_qps.append(cnt * profiles[cpu]['all_batch'][str(agg_batch)])

    cpu_total_qps = sum(cpu_qps)
    gpu_large_qps = gpu_qps * (1-agg_small) / (1-agg_time)
    max_qps = cpu_total_qps / agg_small
    gpu_large_target =  max_qps - cpu_total_qps

    if gpu_large_target >= gpu_large_qps * num1:
        # meaning GPU becomes bottleneck, extra CPUs are useless
        upperbound = gpu_large_qps * num1 / (1-agg_small)
        return Results(key, total_price, upperbound)
    else:
        # all CPUs are fully used to process smaller batch queries
        gpu_usage = gpu_large_target / (gpu_large_qps * num1)
        extra_qps = gpu_qps * num1 * (1-gpu_usage)
        return Results(key, total_price, max_qps + extra_qps)
    
usable_cores = os.sched_getaffinity(0) 
ubs = Parallel(n_jobs=len(usable_cores))(delayed(inner_loop)(num1,num2,num3,num4) for num1, num2, num3, num4 in product(range(0,max_num[0]+1), range(0,max_num[1]+1), range(0,max_num[2]+1), range(0,max_num[3]+1)))
ubs = [k for k in ubs if k is not None]
output = {}
for ub in ubs:
    output[ub.key] = [round(ub.cost,3), ub.ub]
output = dict(sorted(output.items(), key=lambda item: item[1][1], reverse=True))
print('finished')
Path('upperbounds').mkdir(parents=True, exist_ok=True) 
with open(f'upperbounds/{args.model}.json','w') as fp:
    json.dump(output, fp, indent=4)
