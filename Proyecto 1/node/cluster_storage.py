from asyncio.windows_events import NULL
from unicodedata import name
import config 
import pickle
import hashlib

cluster = {}

def add(port):
    global cluster
    if not ("ports" in cluster):
        cluster["ports"] = []
    cluster[port] = [] 
    cluster["ports"].append(port)
    print(cluster)
    save()

def define_ranges():
    j = 1
    size = len(cluster["ports"])

    for i in cluster["ports"]:
        cluster[i].append(int(65536/(size)) * j) 
        j = j + 1
    cluster[i].pop(0)
    cluster[i].append(65536)

    for i in range(1, len(cluster["ports"])):
        cluster[cluster["ports"][i]].append(cluster["ports"][i - 1])
    cluster[cluster["ports"][0]].append(cluster["ports"][-1])

    print(cluster)
    save()

def hash_name(name):
    encoded_name = name.encode("utf-8")
    hash_encoded_name = hashlib.sha1(encoded_name).hexdigest()

    return int(hash_encoded_name[:4], 16)

def redirect(key):
    key = hash_name(key)
    for i in cluster:
        if cluster[i][0] > key:
            break
    print("redirecting to node -> ", i)
    return i

def save():
    cluster_file = open(config.get_cluster_path(nameG), 'wb')
    pickle.dump(cluster, cluster_file)
    cluster_file.close()

def load(name):
    global cluster, cluster_file, nameG
    nameG = name

    try:
        cluster_file = open(config.get_cluster_path(name), 'rb')
        cluster = pickle.load(cluster_file)
        cluster_file.close()
        return False

    except FileNotFoundError:
        cluster = {}
        return True