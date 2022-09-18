# implements Kafka topic consumer functionality

from datetime import datetime
import math
import multiprocessing
from random import randrange
import sqlite3
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
from flask import request
import json
from producer import proceed_to_deliver


_requests_queue: multiprocessing.Queue = None
x_coord = 0
y_coord = 0
z_coord = 0            

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        global x_coord
        global y_coord
        global z_coord
        delivery_required = False
        if details['operation'] == 'move_to':
            print(x_coord)
            print(y_coord)
            dx_target = details['x1'] - x_coord
            dy_target = details['y1'] - y_coord
            print(dx_target)
            print(dy_target)
            details['direction'] = math.atan2(dy_target, dx_target)
            details['distance'] = math.sqrt(dx_target**2 + dy_target**2)
            details['deliver_to'] = 'dispatcher'
            details['operation'] = 'parameters'
            delivery_required = True
        elif details['operation'] == 'nonexistent':
            x_coord += math.cos(details['direction']) * details['distance']
            y_coord += math.sin(details['direction']) * details['distance']
            z_coord = details['z']
            if (round(x_coord,-1) == round(details['x1'],-1)) and (round(y_coord,-1) == round(details['y1'],-1)):
                details['deliver_to'] = 'dispatcher'
                details['operation'] = 'spraying'
                delivery_required = True
            if (round(x_coord,-1) == 0) and (round(y_coord,-1) == 0):
                details['deliver_to'] = 'dispatcher'
                details['operation'] = 'operation_status'
                delivery_required = True
        elif details['operation'] == 'nonexistent2':
            #x_coord = details['x2']
            #y_coord = details['y2']
            x_coord = details['x']
            y_coord = details['y']
            print(x_coord)
            print(y_coord)
            
        elif details['operation'] == 'where_am_i':
            details['x'] = x_coord
            details['y'] = y_coord
            details['z'] = z_coord
            details['deliver_to'] = 'dispatcher'
            details['operation'] = 'coordinates'
            delivery_required = True
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config):
    # Create Consumer instance
    document_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(document_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            document_consumer.assign(partitions)

    # Subscribe to topic
    topic = "position"
    document_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = document_consumer.poll(1.0)
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
        document_consumer.close()


def start_consumer(args, config):
    threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':
    start_consumer(None)
