from hashlib import sha256
import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
import threading

host_name = "0.0.0.0"
port = 6008

app = Flask(__name__)             # create an app instance


@app.route("/activate", methods=['POST'])
def activate():
    content = request.json
    auth = request.headers['auth']

    #todo security: network level
    if auth != 'very-secure-token':
        return "unauthorized", 401

    try:
        pass
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400
    return jsonify({"operation": "ordering requested", "id": req_id})

def start_rest():
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()