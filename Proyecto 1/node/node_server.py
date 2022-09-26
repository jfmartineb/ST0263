from urllib import request
from fastapi import FastAPI, Response, status
from pydantic import BaseModel

import cluster_storage

from requests import get, post, delete
from json import dumps

app = FastAPI()

class Item(BaseModel):
    key: str
    value: str

@app.get("/beatAll", status_code=200)
async def get_kv():
    cluster_storage.beatAll()
    return True 

@app.get("/beat", status_code=200)
async def get_kv():
    return True  

@app.post("/", status_code=201)
async def set_kv(item: Item, response: Response):
    i = cluster_storage.redirect(item.key)
    replica = cluster_storage.find_replica(i)
    string = "http://localhost:" + i
    stringR = "http://localhost:" + replica
    request = string + "/?key=" + item.key

    if (cluster_storage.getPortState(i) == 1):
        request = string + "/?key=" + item.key
        response = get(request.replace(" ",""))

        if response.text is not None:
            response.status_code = status.HTTP_200_OK

        dato = {"key": str(item.key), "value": str(item.value)}
        request2 = string+"/"
        response2 = post(request2.replace(" ",""), data=dumps(dato))
        request2R = stringR + "/repl"
        responseR = post(request2R.replace(" ",""), data=dumps(dato))

    elif (cluster_storage.getPortState(replica) == 1):
        request = stringR + "repl?key=" + item.key
        response = get(request.replace(" ",""))

        if response.text is not None:
            response.status_code = status.HTTP_200_OK

        request2R = stringR + "/repl"
        responseR = post(request2R.replace(" ",""), data=dumps(dato))
        response2 = responseR
    
    else: 
        print("Nodes disconnected")
        response.status_code = status.HTTP_404_NOT_FOUND

    return response2.text


@app.get("/", status_code=200)
async def get_kv(key: str, response: Response):
    i = cluster_storage.redirect(key)
    string = "http://localhost:" + i
    replica = cluster_storage.find_replica(i)
    stringR = "http://localhost:" + replica

    if (cluster_storage.getPortState(i) == 1):
        print("Getting from original")
        request = string + "/?key=" + key
        response = get(request.replace(" ",""))
        if str(response)[11:-2] == "404":
            response.status_code = status.HTTP_404_NOT_FOUND

    elif (cluster_storage.getPortState(replica) == 1):
        print("Getting from replica")
        request = stringR + "/repl/?key=" + key
        print(request)
        response = get(request.replace(" ",""))
        if str(response)[11:-2] == "404":
            response.status_code = status.HTTP_404_NOT_FOUND

    else: 
        print("Nodes disconnected")
        response.status_code = status.HTTP_404_NOT_FOUND
        return " "

    return response.text


@app.delete("/", status_code=200)
async def del_kv(key: str, response: Response):
    i = cluster_storage.redirect(key)
    string = "http://localhost:" + i
    replica = cluster_storage.find_replica(i)
    stringR = "http://localhost:" + replica

    if (cluster_storage.getPortState(i) == 1):
        request = string + "/?key=" + key
        response = delete(request.replace(" ",""))
        requestR = stringR + "/?key=" + key
        responseR = delete(requestR.replace(" ",""))

        if str(response)[11:-2] == "404":
            response.status_code = status.HTTP_404_NOT_FOUND

    elif (cluster_storage.getPortState(replica) == 1):
        requestR = stringR + "/?key=" + key
        responseR = delete(requestR.replace(" ",""))
        if str(responseR)[11:-2] == "404":
            responseR.status_code = status.HTTP_404_NOT_FOUND

    else: 
        print("Nodes disconnected")
        response.status_code = status.HTTP_404_NOT_FOUND

    return '{}'