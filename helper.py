import numpy as np
import pdb

def random_samp(num_samp): 
    # replaying the trace from DeepRecSys ISCA
    mu, sigma = 5.1, 0.2 # mean and standard deviation
    samples = np.random.lognormal(mu, sigma, num_samp)
    
    for i in range(len(samples)):
        rand_num = np.random.randint(low=1,high=100,size=1)
        if rand_num <= 8: 
            samples[i] = np.random.randint(low=1,high=100,size=1)
        elif rand_num <= 30: 
            samples[i] = np.random.randint(low=200,high=600,size=1)
        elif rand_num <= 35: 
            samples[i] = np.random.randint(low=600,high=1000,size=1)
        # make sure the rest 65% goes between 100-200
        elif samples[i] > 200 or samples[i] < 100:
            samples[i] = np.random.randint(low=190,high=200,size=1)
    return samples

# create instance class
class Instance:
    def __init__(self, index, **kwargs): # curr_time, ins_type and price_dict
        self.index = index # ith instance
        self.ins_type = kwargs['ins_type'][index]
        self.price = kwargs['price_dict'][self.ins_type]
        self.curr_query = None
        self.available = True
        self.avail_time = kwargs['curr_time']
    def start(self, query, latency, curr_time):
        self.curr_query = query
        self.available = False
        self.avail_time = latency + curr_time
    def update(self, curr_time): # run this after each clock tick
        if self.available:
            self.avail_time = curr_time
    def request_done(self, curr_time):
        self.available = True
        self.curr_query = None
        self.avail_time = curr_time

# create query class
class Query:
    def __init__(self, query, curr_time, **kwargs): # curr_time, ins_type and price_dict
        self.query = query # ith instance
        self.batch = kwargs['batch']
        self.lats = kwargs['lats']
        self.lats_est = kwargs['lats_est']
        self.t_arrive = curr_time
        self.qos = kwargs['qos']
        self.t_qos = self.qos # time left till QoS
        self.wait = 0
    def update(self, curr_time): # run this to update time till qos, do this before starting query 
        t_passed = curr_time - self.t_arrive
        self.wait = t_passed
        if t_passed >= self.qos: # jobs are all the same once violated
            self.t_qos = 0
        else:
            self.t_qos = self.qos - t_passed

class Future_query:
    def __init__(self, query, lats, arr):
        self.query = query
        self.lats = lats
        self.arr = arr

class Oracle_query:
    def __init__(self, query, lats, qos):
        self.query = query
        self.lats = lats
        self.qos = qos

class Ins_Bipartite:
    def __init__(self, index, **kwargs): # curr_time, ins_type and price_dict
        self.index = index # ith instance
        self.ins_type = kwargs['ins_type'][index]
        self.price = kwargs['price_dict'][self.ins_type]
        self.curr_query = None
        self.available = True
        self.avail_time = kwargs['curr_time']
        self.t_left = 0
        self.t_left_est = 0
        self.skew = 1
    def start(self, query, latency, latency_est, curr_time):
        self.curr_query = query
        self.available = False
        self.avail_time = latency + curr_time # real available time
        self.t_left = latency
        self.t_left_est = latency_est
    def update(self, curr_time): # run this after each clock tick
        if self.available: # there is no query
            self.avail_time = curr_time
        else: # there is a query running
            t_left_prev = self.t_left
            self.t_left = self.avail_time - curr_time
            passed_time = t_left_prev - self.t_left
            self.t_left_est -= passed_time
            if self.t_left_est < 0:
                self.t_left_est = 0
    def request_done(self, curr_time):
        self.available = True
        self.curr_query = None
        self.avail_time = curr_time
        self.t_left = 0
        self.t_left_est = 0        











