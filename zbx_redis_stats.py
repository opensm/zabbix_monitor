#!/usr/local/python/shims/python
from rediscluster import StrictRedisCluster

import redis
import sys
#import mylog

redis_nodes = [{'host': 'ip', 'port': port},
               {'host': 'ip', 'port': port},
               {'host': 'ip', 'port': port},
               {'host': 'ip', 'port': port},
               {'host': 'ip', 'port': port},
               {'host': 'ip', 'port': port},
               ]

###
# 进入redis集群模式，如果异常，记录到日志中，并终止脚本
###

try:
    redisconn = StrictRedisCluster(startup_nodes=redis_nodes, password='pwd')

except Exception as e:
    print('%s' % e)
    sys.exit(0)

###
# 定义参数
###


data = {}
NodeData = {}
hit = 0
misshit = 0
hitrate = 0.00


###
# 定义函数，抓取监控项
###


def ClusterState(item):
    cluster_state = redisconn.execute_command('cluster', 'info')
    cluster_state = cluster_state.split('\r\n')
    try:
        for i in cluster_state:
            data[i.split(':')[0]] = i.split(':')[1]
    except:
        pass
    if item == 'clusterstatus':
        state = data['cluster_state']
        if state == 'ok':
            item = 1
        else:
            item = 0
        return item

    elif item == 'clusterslotsfail':
        item = data['cluster_slots_fail']
        return item

    elif item == 'clusterknownnodes':
        item = data['cluster_known_nodes']
        return item
    else:
        return 9999


def NodeInfoServer(item):
    node_info = redisconn.info('Server')
    NodeData = node_info['ip:port']
    if item == 'uptime_in_days':
        item = NodeData['uptime_in_days']
        return item
    else:
        return 9999


def NodeInfoClients(item):
    node_info = redisconn.info('Clients')
    NodeData = node_info['ip:port']
    if item == 'connected_clients':
        item = NodeData['connected_clients']
        return item
    else:
        return 9999


def NodeInfoMemory(item):
    node_info = redisconn.info('Memory')
    NodeData = node_info['ip:port']
    if item == 'used_memory_human':
        item = NodeData['used_memory_human']
        return item
    elif item == 'total_system_memory_human':
        item = NodeData['total_system_memory_human']
        return item
    else:
        return 9999


def NodeInfoPersistence(item):
    node_info = redisconn.info('Persistence')
    NodeData = node_info['ip:port']

    if item == 'rdb_last_bgsave_status':
        item = NodeData['rdb_last_bgsave_status']
        if item == 'ok':
            item = 1
        else:
            item = 0
        return item
    else:
        return 9999


def NodeInfoStats(item):
    node_info = redisconn.info('Stats')
    NodeData = node_info['ip:port']
    if item == 'instantaneous_ops_per_sec':
        item = NodeData['instantaneous_ops_per_sec']
        return item
    elif item == 'instantaneous_input_kbps':
        item = NodeData['instantaneous_input_kbps']
        return item
    elif item == 'instantaneous_output_kbps':
        item = NodeData['instantaneous_output_kbps']
        return item
    elif item == 'hit':
        hit = NodeData['keyspace_hits']
        misshit = NodeData['keyspace_misses']
        hitrate = round((float(hit) / float(hit + misshit)), 3)
        item = hitrate
        return item
    else:
        return 9999


###
# 脚本传参，zabbix获取监控项
###

if sys.argv[1] == 'status':
    print(ClusterState('clusterstatus'))
elif sys.argv[1] == 'slotsfail':
    print(ClusterState('clusterslotsfail'))
elif sys.argv[1] == 'nodes':
    print(ClusterState('clusterknownnodes'))
elif sys.argv[1] == 'day':
    print(NodeInfoServer('uptime_in_days'))
elif sys.argv[1] == 'clients':
    print(NodeInfoClients('connected_clients'))
elif sys.argv[1] == 'usememory':
    print(NodeInfoMemory('used_memory_human'))
elif sys.argv[1] == 'sysmemory':
    print(NodeInfoMemory('total_system_memory_human'))
elif sys.argv[1] == 'rdb':
    print(NodeInfoPersistence('rdb_last_bgsave_status'))
elif sys.argv[1] == 'ops':
    print(NodeInfoStats('instantaneous_ops_per_sec'))
elif sys.argv[1] == 'input_kbps':
    print(NodeInfoStats('instantaneous_input_kbps'))
elif sys.argv[1] == 'output_kbps':
    print(NodeInfoStats('instantaneous_output_kbps'))
elif sys.argv[1] == 'hit':
    print(NodeInfoStats('hit'))
