# Kairos: Building Cost-Efficient Machine Learning Inference Systems with Heterogeneous Cloud Resources

The 32nd ACM International Symposium on High-Performance Parallel and Distributed Computing (HPDC'23)

### Set up environment

```
pip install -r requirements.txt
```
Decompress the ``data.tar.gz`` file which contains cloud operation data that can be used to run locally

```
tar -xf data.tar.gz
```

### Kairos query distributor

Kairos performs optimal query distribution given a fixed heterogeneous configuration which is set in ``config.json``. The ``config.json`` file configures the number of instances to use in the heterogeneous server. Start the inference servers in a service node:

```
python launch_servers.py
```

From another node, run 
```
python kairos_query_distributor
```
The output will show that Kairos provides a much higher throughput than a naive query distributor, while having 99\% of queries to meet QoS. The arrival rate argument in the script controls request rate, reduce it to further increase the throughput.

### Kairos resource allocator

Run the following script

```
python kairos_resource_allocator.py
```
This calculates and ranks the upperbounds of all possible heterogeneous configurations without any online exploration. The results are stored in the ``upperbounds`` folder. In each result saved as .json format, the key represents the heterogeneous configuration, and the value is a list of the ``[cost, upperbound]`` for the corresponding configuration.

### Note
You can reach me at my email: li.baol@northeastern.edu

