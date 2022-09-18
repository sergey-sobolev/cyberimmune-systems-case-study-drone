from hashlib import sha256
import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 6009

app = Flask(__name__)             # create an app instance


_requests_queue: multiprocessing.Queue = None

@app.route("/activate", methods=['POST'])
def activate():
    content = request.json
    auth = request.headers['auth']

    #todo security: network level
    if auth != 'very-secure-token':
        return "unauthorized", 401

    req_id = uuid4().__str__()

    try:
        print(content)
        ordering_details = {
            "id": req_id,
            "operation": "activate",
            "deliver_to": "dispatcher",
            "source": "connector",
            "activate": True
            }
        _requests_queue.put(ordering_details)
        print(f"activating event: {ordering_details}")
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "ordering requested", "id": req_id})

@app.route("/deactivate", methods=['POST'])
def deactivate():
    content = request.json
    auth = request.headers['auth']

    #todo security: network level
    if auth != 'very-secure-token':
        return "unauthorized", 401

    req_id = uuid4().__str__()

    try:
        print(content)
        ordering_details = {
            "id": req_id,
            "operation": "deactivate",
            "deliver_to": "monitor",
            "source": "connector",
            "activate": True
            }
        _requests_queue.put(ordering_details)
        print(f"activating event: {ordering_details}")
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "ordering requested", "id": req_id})

@app.route("/new-task", methods=['POST'])
def ordering():
    content = request.json
    auth = request.headers['auth']

    #todo security: network level
    if auth != 'very-secure-token':
       return "unauthorized", 401

    req_id = uuid4().__str__()

    try:
        print(content)
        ordering_details = {
            "id": req_id,
            "operation": "task",
            "deliver_to": "dispatcher",
            "source": "connector",
            "x1": content['x1'],
            "y1": content['y1'],
            "z1": content['z1'],
            "expenditure": content['expenditure'],
            "x2": content['x2'],
            "y2": content['y2'],
            "z2": content['z2'],
            "close_key": content['close_key']
            }
        _requests_queue.put(ordering_details)
        print(f"new task: {ordering_details}")
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "ordering requested", "id": req_id})

def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()