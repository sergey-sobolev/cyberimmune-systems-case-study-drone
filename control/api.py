from hashlib import sha256
import json
import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading
from urllib.request import urlopen, Request
import requests
import socket

host_name = "0.0.0.0"
port = 6004

app = Flask(__name__)             # create an app instance


@app.route("/task", methods=['GET'])
def task():
    content = request.json
    auth = request.headers['auth']

    #todo security: network level
    if auth != 'very-secure-token':
       return "unauthorized", 401

    try:
        #print(content)
        header_auth_token = "very-secure-token"
        request_body = {
            "x1": 50,
            "y1": 50,
            "z1": 10,
            "expenditure": 10,
            "x2": 55,
            "y2": 55,
            "z2": 10,
            "close_key": 12345
        }
        headers = {'content-type': 'application/json', 'auth': header_auth_token}
        #req = Request('http://0.0.0.0:6009/new-task', data=json.dumps(request_body).encode(), headers=headers)
        #print(req)
        try:
            #urlopen(req)
            socket.create_connection(('0.0.0.0', 6009), timeout=3)
            r = requests.post('http://10.5.1.2:6009/activate', request_body)
            print(r)
        except Exception as e:
            print(e)
            return error_message, 400
        #print(resp)
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "new order"})

def start_rest():
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()