# implements Kafka topic consumer functionality

from cgitb import reset
from datetime import datetime
import math
import multiprocessing
from random import randrange
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
from flask import request
import json
from producer import proceed_to_deliver
from urllib.request import urlopen, Request
import requests
_requests_queue: multiprocessing.Queue = None
import socket            

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        delivery_required = False
        if details['operation'] == 'ask_task':
            pass
            print('[info] here sended message to server about successfull activation')
            # print("here am i")
            # header_auth_token = "very-secure-token"
            # request_body = {
            #     "status": "active"
            # }
            # headers = {'content-type': 'application/json', 'auth': header_auth_token}
            # #req = Request('http://0.0.0.0:6004/task', data=json.dumps(request_body).encode(), headers=headers)
            # #print(req)
            # #urlopen(req)
            # #socket.create_connection(('0.0.0.0', 6004), timeout=3)
            # resp = requests.get('http://10.5.1.1:6004/task', timeout=3)
            # print(resp)
        elif details['operation'] == 'error':
            #response = request.post('https://localhost:6004/confirmation', json={'status':'successfull'})
            print('[info] error successfully catched during the work')
            pass
        elif details['operation'] == 'log':
            print('[info] here sended message to server with work logs')
            pass
        elif details['operation'] == 'operation_status':
            print('[info] task was successfully ended, map inside this message')
            pass
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    connector_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(connector_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            connector_consumer.assign(partitions)

    # Subscribe to topic
    topic = "connector"
    connector_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = connector_consumer.poll(1.0)
            if msg is None:
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    handle_event(id, details_str)
                except Exception as e:
                    print(
                        f"[error] Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        connector_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
