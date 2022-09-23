from argparse import ArgumentParser, FileType
from configparser import ConfigParser
import threading
from time import sleep
import time
import pytest
import re
import json
from urllib.request import urlopen, Request
from uuid import uuid1
import requests
from kafka import KafkaConsumer, KafkaProducer
import sys


messages = []



def listener(event):
    #next shit really readed all stack, I think, 
    consumer = KafkaConsumer(
            bootstrap_servers=['localhost:9094'], auto_offset_reset='latest'
        )
    consumer.subscribe('monitor')
    global messages
    while not event.is_set():
        try:
            records = consumer.poll(timeout_ms=1000)
            for topic_data, consumer_records in records.items():
                for consumer_record in consumer_records:
                    messages.append(consumer_record.value.decode('utf-8'))
                    #print("Received message: " + str(consumer_record.value.decode('utf-8')))
            continue
        except Exception as e:
            print(e)
            continue

###Activate tests

def deactivate():
    data = {
        "somedata": "test"
    }
    response = requests.post(
        "http://0.0.0.0:6009/deactivate",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )    

def activate():
    data = {
        "somedata": "test"
    }
    response = requests.post(
        "http://0.0.0.0:6009/activate",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )

def test_activate():
    data = {
        "somedata": "test"
    }
    response = requests.post(
        "http://0.0.0.0:6009/activate",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )
    assert response.status_code == 200
    deactivate()
    

def test_asking_task():
    sleep(5)
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    time.sleep(5)
    activate()
    sleep(1)
    event.set()
    thread.join()
    global messages
    assert len(messages) == 2
    details = json.loads(str(messages[0]))
    details1 = json.loads(str(messages[1]))
    assert details['id'] == details1['id'] # id
    #assert (messages[0]['activate'] == True) or (messages[1]['activate'] == True)
    messages = []
    deactivate()

def test_write_order():
    sleep(5)
    event = threading.Event()
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    time.sleep(5)
    activate()
    sleep(1)
    event.set()
    thread.join()
    global messages
    details = json.loads(str(messages[0]))
    assert (details['operation'] == 'activate')
    details = json.loads(str(messages[1]))
    assert (details['operation'] == 'ask_task') # operation
    messages = []
    deactivate()

### Action tests
def send_task():
    data = {
        "x1": 50,
        "y1": 50,
        "z1": 10,
        "expenditure": 10,
        "x2": 55,
        "y2": 55,
        "z2": 10,
        "close_key": 12345
    }
    response = requests.post(
        "http://0.0.0.0:6009/new-task",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )


def test_success_result():
    sleep(10)
    event = threading.Event()
    activate()
    time.sleep(5)
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    time.sleep(5)
    send_task()
    time.sleep(120)
    event.set()
    thread.join()
    global messages
    assert len(messages) == 13
    details = json.loads(str(messages[0]))
    details1 = json.loads(str(messages[len(messages)-1]))
    assert details['id'] == details1['id'] # id
    assert (details1['operation'] == 'operation_status')
    messages = []
    deactivate()

def test_surface_result():
    time.sleep(10)
    event = threading.Event()
    activate()
    time.sleep(5)
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    time.sleep(5)
    send_task()
    time.sleep(120)
    event.set()
    thread.join()
    global messages
    details = json.loads(str(messages[len(messages)-1]))
    fields_max = 300/details['expenditure']
    fields = 0
    for s in details['surface']:
        for f in s:
            if f == 'X': 
                fields+=1
    assert fields_max >= fields 
    messages = []
    deactivate()



    ### security tests

def test_activate_without_token():
    time.sleep(10)
    data = {
        "somedata": "test"
    }
    response = requests.post(
        "http://0.0.0.0:6009/activate",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "blablabla"},
    )
    assert response.status_code == 401
    deactivate()

def send_wrong_task():
    data = {
        "x1": 50,
        "y1": 50,
        "z1": 10,
        "expenditure": 10,
        "x2": 55,
        "y2": 55,
        "z2": 10,
        "close_key": 5467
    }
    response = requests.post(
        "http://0.0.0.0:6009/new-task",
        data=json.dumps(data),
        headers={"Content-Type": "application/json", "auth": "very-secure-token"},
    )

def test_bruteforce():
     time.sleep(10)
     event = threading.Event()
     activate()
     time.sleep(5)
     thread = threading.Thread(target=lambda: listener(event))
     thread.start()
     time.sleep(5)
     send_wrong_task()
     time.sleep(1)
     send_wrong_task()
     time.sleep(1)
     send_wrong_task()
     time.sleep(1)
     send_wrong_task()
     time.sleep(3)
     event.set()
     thread.join()
     global messages
     details = json.loads(str(messages[len(messages)-1]))
     assert details['operation'] == 'error' # id
     assert details['err_msg'] == 'Task is under bruteforce!'
     messages = []
     deactivate()

def test_repeated_task():
    time.sleep(10)
    event = threading.Event()
    activate()
    time.sleep(5)
    thread = threading.Thread(target=lambda: listener(event))
    thread.start()
    time.sleep(5)
    send_task()
    time.sleep(2)
    send_task()
    time.sleep(2)
    event.set()
    thread.join()
    global messages
    #print(messages)
    details = json.loads(str(messages[len(messages)-1]))
    assert details['operation'] == 'task'
    messages = []
    deactivate()

    
