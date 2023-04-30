# Kairos: Building Cost-Efficient Machine Learning Inference Systems with Heterogeneous Cloud Resources

The 32nd ACM International Symposium on High-Performance Parallel and Distributed Computing (HPDC'23)

### Set up environment

```
pip install -r requirements.txt
```
### Kairos query distributor

Kairos performs optimal query distribution given a fixed heterogeneous configuration (set in ``config.json``). Start the inference servers in a service node:

```
python launch_servers.py
```

From another node, run 
```
python kairos_query_distributor
```
The output will show that Kairos provides a much higher throughput than a naive query distributor.

### Kairos resource allocator

Run the following script

```
python kairos_resource_allocator.py
```
This calculates and ranks the upperbounds of all possible heterogeneous configurations without any online exploration. The results are stored in the ``upperbounds`` folder.

### Note
You can reach me at my email: li.baol@northeastern.edu

