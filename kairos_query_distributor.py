import pandas
import numpy as np
import sys
import json
import os
import math
import random
import time
import helper
from helper import Ins_Bipartite, Query, Instance
from scipy.optimize import linear_sum_assignment
import grpc
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]
if f'{str(ROOT)}/grpc' not in sys.path:
    sys.path.append(f'{str(ROOT)}/grpc')
import grpc_pb2, grpc_pb2_grpc
import argparse

class Kairos_Query_Distributor:
    def __init__(self, args) -> None:
        with open('service_addr.json') as f:            
            self.service_addr = json.load(f)
        with open('config.json') as f:
            self.config = json.load(f)    
        self.lat_dict = {} # {'c5a.2xlarge': [array1, array2, ...]} each array correspond to a batch size
        for ins in self.config: 
            self.lat_dict[ins] = {}
            for batch in range(10, 1001, 10):
                path = f'data/{ins}/{args.model}_{batch}_1.json'
                path_load = f'data/logs_load/{ins}/{args.model}_{batch}_1.json'
                with open(path, 'r') as f:
                    lat_list = json.load(f)
                with open(path_load, 'r') as f_load:
                    load_list = np.asarray(json.load(f_load))
                total_lat = lat_list + load_list
                filter_lat = np.delete(total_lat, total_lat.argmax())
                self.lat_dict[ins][batch] = np.mean(filter_lat)
        with open('service_addr.json') as f:
            service_addr = json.load(f)
        self.ins_stubs = []
        self.channels = []
        for i in service_addr:
            channel = grpc.insecure_channel(i)
            self.channels.append(channel)
            stub = grpc_pb2_grpc.SchedulerStub(channel)
            self.ins_stubs.append(stub)

    def terminate(self):
        for channel in self.channels:
            channel.close()

    def run(self, args, max_batch = 1000): # p is for printing
        def callback(response):
            # upon response, update the instance availability
            idx = response.idx
            q_wait = response.q_wait
            lat = response.exe_time
            curr_time = time.time()*1000
            ins_list[idx].request_done(curr_time)
            # check for violation
            if lat + q_wait <= args.qos:
                violation.append(0)
            else: # violation
                violation.append(1)

        safeguard = 0.02 * args.qos

        price_file = 'price.csv'
        price = pandas.read_csv(price_file)
        instance_list = price[price.columns[0]].tolist()
        price_list = price[price.columns[1]].tolist()
        price_dict = {}
        for i in range(len(instance_list)):
            price_dict[instance_list[i]] = price_list[i]

        queue_time = [] # this is the arrival time of each query
        arrival_time = 0 
        for i in range(args.num_samp):
            arrival_time += np.random.poisson(args.inter_arrival_kairos) # time in ms
            queue_time.append(arrival_time)
        query = 0 # pointer to next query to arrive
        
        samples = helper.random_samp(args.num_samp) 
        
        curr_time = time.time()*1000
        
        ins_type = []
        for k,v in self.config.items():
            ins_type += [k]*v
        num_ins = len(ins_type)

        violation = [] # 0: no violation. 1: violation

        pending_q = [] # queue for queries that arrive
        ins_list = [Ins_Bipartite(i, ins_type=ins_type, price_dict=price_dict, curr_time=curr_time) for i in range(num_ins)]        
        total_price = sum([(k.price) for k in ins_list])

        norm_ins = ins_list[0].ins_type # the first instance must be a base instance
        norm_lat = np.mean(self.lat_dict[norm_ins][math.ceil(max_batch/10)*10])
        for ins in ins_list:
            key = ins.ins_type
            lat = np.mean(self.lat_dict[key][math.ceil(max_batch/10)*10])
            ins.skew = round((norm_lat / lat),2) # heterogeneity coefficient

        TIME_START = time.time()*1000 # big bang time in ms

        while True: 
            # FIFO queue, always makes sure queries get served by coming order            
            while True: # when query arrive at same time, add all to queue
                if query < args.num_samp:                    
                    if queue_time[query] + TIME_START <= curr_time:
                        batch = math.ceil(samples[query]/10)*10                        
                        lats_est = {}
                        for key in self.config:
                            lats_est[key] = round(np.mean(self.lat_dict[key][batch]))
                        curr_time = time.time()*1000
                        pending_q.append(Query(query,curr_time,batch=batch,lats=lats_est,lats_est=lats_est,qos=args.qos))
                        query += 1
                    else:
                        break
                else:
        #            print('no more queries')
                    break
            avail_ins = [k for k in ins_list if k.available == True]

            if args.qos > 0:
                if len(pending_q) > args.qos / args.inter_arrival_kairos * 10 and len(pending_q) > 2 * num_ins: # when queries stack up
                    print('queries stack too many in queue')
                    return total_price, 0

            if len(pending_q) > 0 and len(avail_ins) > 0:
                # construct graph matrix
                num_q = len(pending_q)
                if num_q > 2*num_ins: # limit number of queries in queue to reduce computation
                    num_q = 2*num_ins
                cost = np.empty([num_q, num_ins])
                # max flow algorithm to maximize the slack sum on instances
                for i in range(num_q):
                    for j in range(num_ins):
                        # if possible to meet QoS, punish violation
                        # if not possible, just let cost be negative
                        slack = ins_list[j].skew * (- ins_list[j].t_left_est - pending_q[i].lats_est[ins_list[j].ins_type]) # this is slack on instance
                        resi = pending_q[i].t_qos - ins_list[j].t_left_est - pending_q[i].lats_est[ins_list[j].ins_type] # this is residual on query
                        resi_safe = resi - safeguard

                        # this simply avoids serving query using instance that violates QoS
                        if resi_safe < 0 and pending_q[i].t_qos > 0 and resi >= 0: 
                            slack = -1000 / 2
                        elif resi_safe < 0 and pending_q[i].t_qos > 0:
                            slack = -1000

                        cost[i,j] = -slack # minus because scipy.lsa is doing minimization

                row_ind, col_ind = linear_sum_assignment(cost)

                del_ind = []
                curr_time = time.time()*1000
                for i, j in zip(row_ind, col_ind): # each pair is a mapping
                    if ins_list[j].available == True: # only schedule on available ones
                        q_serve = pending_q[i]
                        q_wait = q_serve.wait
                        del_ind.append(i)
                        lat = q_serve.lats[ins_list[j].ins_type]
                        lat_est = q_serve.lats_est[ins_list[j].ins_type]
                        
                        ins_list[j].start(q_serve.query, lat, lat_est, curr_time)
                        # send gRPC request to server j here
                        response_future = self.ins_stubs[j].Serve.future(grpc_pb2.JobMessage(batch=q_serve.batch,q_wait=q_wait))
                        response_future.add_done_callback(lambda future: callback(future.result()))

                if len(violation) >= 100:
                    realtime_vio = len([k for k in violation if k != 0]) / len(violation) * 100
                    if realtime_vio > 10:
                        print('violation rate too high, early termination')
                        return total_price, 0

                for i in sorted(del_ind, reverse=True):
                    del pending_q[i]

            avail_ins = [k for k in ins_list if k.available == True]

            curr_time = time.time()*1000
            [k.update(curr_time) for k in ins_list]
            [k.update(curr_time) for k in pending_q]

            if query == args.num_samp and len(pending_q) == 0:# and len(avail_ins) == len(ins_list):
                break

        vio_array = np.array(violation)
        non_vio = (vio_array == 0).sum() / len(vio_array) * 100
        lat_vio = (vio_array == 1).sum() / len(vio_array) * 100
        throughput = 1000 * args.num_samp / (time.time()*1000 - TIME_START) # qps

        if not args.silent:
            print('================================')
            print(f'Result of KAIROS query distributor:')
            print(f'number of instances: {num_ins}')
            print(f'instance type: {self.config}')
            print(f'cloud cost: ${total_price}/hr')
            print(f'non violation: {non_vio}%')
            print(f'lat violation: {lat_vio}%')
            print(f'throughput QPS: {throughput}')
            print('================================')

        output = {}
        output['total_price'] = round(total_price,2)
        output['non_vio'] = round(non_vio,2)

        return output['total_price'], output['non_vio']

    def fcfs(self, args): # p is for printing
        def callback(response):
            # upon response, update the instance availability
            idx = response.idx
            q_wait = response.q_wait
            lat = response.exe_time
            curr_time = time.time()*1000
            ins_list[idx].request_done(curr_time)
            # check for violation
            if lat + q_wait <= args.qos:
                violation.append(0)
            else: # violation
                violation.append(1)

        price_file = 'price.csv'
        price = pandas.read_csv(price_file)
        instance_list = price[price.columns[0]].tolist()
        price_list = price[price.columns[1]].tolist()
        price_dict = {}
        for i in range(len(instance_list)):
            price_dict[instance_list[i]] = price_list[i]

        queue_time = [] # this is the arrival time of each query
        arrival_time = 0 
        for i in range(args.num_samp):
            arrival_time += np.random.poisson(args.inter_arrival_fcfs) # time in ms
            queue_time.append(arrival_time)
        query = 0 # pointer to next query to arrive
        
        samples = helper.random_samp(args.num_samp) 
        
        curr_time = time.time()*1000
        
        ins_type = []
        for k,v in self.config.items():
            ins_type += [k]*v
        num_ins = len(ins_type)

        violation = [] # 0: no violation. 1: violation

        pending_q = [] # queue for queries that arrive
        pending_w = []
        ins_list = [Instance(i, ins_type=ins_type, price_dict=price_dict, curr_time=curr_time) for i in range(num_ins)]
        total_price = sum([(k.price) for k in ins_list])

        TIME_START = time.time()*1000 # big bang time in ms

        while True: 
            # FIFO queue, always makes sure queries get served by coming order            
            while True: # when query arrive at same time, add all to queue
                if query < args.num_samp:                    
                    if queue_time[query] + TIME_START <= curr_time:
                        pending_q.append(query)
                        pending_w.append(time.time()*1000)
                        query += 1
                    else:
                        break
                else:
        #            print('no more queries')
                    break
            avail_ins = [k for k in ins_list if k.available == True]

            if args.qos > 0:
                if len(pending_q) > args.qos / args.inter_arrival_fcfs * 10 and len(pending_q) > 2 * num_ins: # when queries stack up
                    print('queries stack too many in queue')
                    return total_price, 0

            for ins in avail_ins:
                if len(pending_q) > 0:
                    q_serve = pending_q.pop(0)
                    q_wait = time.time()*1000 - pending_w.pop(0)
                    
                    # # need to calculate the latency of the query
                    batch = math.ceil(samples[q_serve]/10)*10  #round(samples[q_serve])
                    # lat = random.choice(lat_dict[ins.ins_type][batch_ind])
                    curr_time = time.time()*1000
                    ins.start(q_serve, 0, curr_time)
                    response_future = self.ins_stubs[ins.index].Serve.future(grpc_pb2.JobMessage(batch=batch,q_wait=q_wait))
                    response_future.add_done_callback(lambda future: callback(future.result()))
                else:
                    break
            avail_ins = [k for k in ins_list if k.available == True]

            curr_time = time.time()*1000
            [k.update(curr_time) for k in ins_list]

            if query == args.num_samp and len(pending_q) == 0:
                break

        vio_array = np.array(violation)
        non_vio = (vio_array == 0).sum() / len(vio_array) * 100
        lat_vio = (vio_array == 1).sum() / len(vio_array) * 100
        throughput = 1000 * args.num_samp / (time.time()*1000 - TIME_START) # qps

        if not args.silent:
            print('================================')
            print(f'Result of FCFS query distributor:')
            print(f'number of instances: {num_ins}')
            print(f'instance type: {self.config}')
            print(f'cloud cost: ${total_price}/hr')
            print(f'non violation: {non_vio}%')
            print(f'lat violation: {lat_vio}%')
            print(f'throughput QPS: {throughput}')
            print('================================')

        output = {}
        output['total_price'] = round(total_price,2)
        output['non_vio'] = round(non_vio,2)

        return output['total_price'], output['non_vio']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='kairos query distributor')
    parser.add_argument('--model', type=str, help='model name, choose from ncf, rm2, wnd, mtwnd, dien', default='rm2')
    parser.add_argument('--num_samp', type=int, help='number of samples', default=20000)    
    parser.add_argument('--inter_arrival_kairos', type=float, help='inter arrival time (ms)', default=10.5)
    parser.add_argument('--inter_arrival_fcfs', type=float, help='inter arrival time (ms)', default=20)
    parser.add_argument('--qos', type=int, help='qos target (ms)', default=350)    
    parser.add_argument('--silent', action='store_true', help='slience output')

    args = parser.parse_args()

    scheduler = Kairos_Query_Distributor(args)
    scheduler.run(args)
    time.sleep(3)
    scheduler.fcfs(args)
    time.sleep(3)
    scheduler.terminate()
