# implements Kafka topic consumer functionality

from atexit import register
from datetime import datetime
import multiprocessing
import random
import sqlite3
import threading
import time
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
import base64


_requests_queue: multiprocessing.Queue = None



class Register:
    battery = 100
    mixture = 100
    surface = []
    allow = False
    x0 = 0
    y0 = 0
    z0 = 0
    x1 = 0
    y1 = 0
    z1 = 0
    activated = False
    attempts = 3
    stopped = False
    expenditure = 0

def move_to(details,x,y,z):
    details['deliver_to'] = 'position'
    details['operation'] = 'move_to'
    details['x1'] = x
    details['y1'] = y
    details['z1'] = z
    proceed_to_deliver(details['id'], details)

#todo same check of mixture level changes to block it

def where_am_i(det):
    time.sleep(5)
    #print('Inside')
    while (Register.activated):
        #print('while')
        det['deliver_to'] = 'position'
        det['operation'] = 'where_am_i'
        proceed_to_deliver(det['id'], det)
        time.sleep(10)

def spraying_start(details):
    while True:
        print(Register.allow)
        if Register.allow:
            details['deliver_to'] = 'sprayer'
            details['operation'] = 'start'
            proceed_to_deliver(details['id'], details)
            break
        else:
            time.sleep(2)

def handle_event(id, details_str):
    details = json.loads(details_str)
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    #print(details)
    try:
        delivery_required = False
        if details['operation'] == 'activate':
            try:
                Register.battery = 100
                Register.mixture = 300
                Register.surface = []
                Register.allow = False
                Register.x1 = 0
                Register.y1 = 0
                Register.z1 = 0
                Register.activated = True
                Register.attempts = 3
                Register.stopped = False
                details['deliver_to'] = 'connector'
                details['operation'] = 'ask_task'
                
            except Exception as e:
                details['err_msg'] = "Can't activate dron!"
                details['deliver_to'] = 'connector'
                details['operation'] = 'error'
            
            delivery_required = True

        elif details['operation'] == 'task':
            try:
                #print({Register.attempts})
                #todo here should be something stronger)))
                if Register.attempts > 0:
                    if details['close_key'] == 12345:
                        Register.expenditure = details['expenditure']
                        print("[info] {} is in working!".format(details['id']))
                        move_to(details, details['x1'], details['y1'], details['z1'])
                        det = details.copy()
                        #threading.Thread(target=lambda: where_am_i(det)).start()
                    else:
                        Register.attempts -= 1
                        print('[warning] wrong password detected!')
                else:
                #     details['err_msg'] = "Bruteforce!"
                #     details['deliver_to'] = 'connector'
                #     details['operation'] = 'error'
                #     delivery_required = True
                     raise Exception("Bruteforce!")
                
            except Exception as e:
                details['err_msg'] = "Task is under bruteforce!"
                details['deliver_to'] = 'connector'
                details['operation'] = 'error'
                delivery_required = True

        elif details['operation'] == 'parameters':
            
            Register.stopped = False
            v_speed = random.randint(1,5)
            speed = random.randint(1,10)
            timestamp = time.time();
            print('[info] taking off {timestamp}')
            time.sleep(abs(Register.z1 - details['z1']) / v_speed) 
            timestamp = time.time();
            print('[info] starting motion {timestamp}')
            journey_time = abs(details['distance'] / speed) 
            timestamp = time.time();
            print(f"[motion] {id}, will take {journey_time} from {timestamp}")

            for i in range(round(journey_time/0.1)-1):
                time.sleep(0.1)
                if Register.stopped:
                    break

            now = time.time()
            det = details.copy()
            det['operation'] = 'nonexistent'
            det['deliver_to'] = 'position'
            det['distance'] = speed * (now - timestamp)
            det['time'] = now - timestamp
            det['z'] = details['z1']
            print(f"[info] {id}, awaited in {now}, went {det['distance']}")
            proceed_to_deliver(id, det)
            delivery_required = False
        
        elif details['operation'] == 'spraying':
            Register.allow = True
            det = details.copy()
            time.sleep(1)
            #det['deliver_to'] = 'sprayer'
            #det['operation'] = 'start'
            #proceed_to_deliver(id, det)
            threading.Thread(target=lambda: spraying_start(det)).start()
            time.sleep(1)
            #print(details)
            #x1 = round(abs(details['x2']-Register.x1))
            #y1 = round(abs(details['y2']-Register.y1))
            #print(x1)
            #print(y1)
            det = []
            det = details.copy()
            #todo correct order and 
            x = abs(details['x2']-details['x1'])
            y = abs(details['y2']-details['y1'])
            Register.surface = [[0]*x for i in range(y)]
            for i in range(x):
                for j in range(y):
                    time.sleep(1)
                    if Register.allow and (Register.mixture >= Register.expenditure):
                        Register.surface[i][j] = 'X'
                        #print(Register.surface[i][j])
                        Register.mixture -= Register.expenditure
                    else: 
                        Register.surface[i][j] = ' '
            #print(Register.surface)
            det['deliver_to'] = 'position'
            det['operation'] = 'nonexistent2'
            det['x'] = details['x2']
            det['y'] = details['y2']
            proceed_to_deliver(id, det)
            details['surface'] = Register.surface
            time.sleep(1)
            move_to(details,0,0,0)
            det = details.copy()
            det['deliver_to'] = 'sprayer'
            det['operation'] = 'stop'
            proceed_to_deliver(id, det)
            delivery_required = False

            
        elif details['operation'] == 'coordinates':
            Register.x1 = details['x']
            Register.y1 = details['y']
            Register.z1 = details['z']
            delivery_required = False
        

        elif details['operation'] == 'obstruction':
            print('[info] obstruction was found in the way')
            Register.allow = False
            details['deliver_to'] = 'sprayer'
            details['operation'] = 'stop'
            proceed_to_deliver(id, details)
            #todo here we are going around 
            time.sleep(1)
            Register.allow = True
            details['deliver_to'] = 'sprayer'
            details['operation'] = 'start'
            delivery_required = True

        elif details['operation'] == 'gps_err':
            Register.allow = False
            details['err_msg'] = "GPS error founded!"
            details['deliver_to'] = 'connector'
            details['operation'] = 'error'
            Register.stopped = True
            move_to(details, Register.x0, Register.y0, Register.z0)
            delivery_required = True
            
        elif details['operation'] == 'operation_status':
            details['deliver_to'] = 'connector'
            delivery_required = True
        else:
            print(f"[warning] unknown operation!\n{details}")                
        if delivery_required:
            proceed_to_deliver(id, details)
    except Exception as e:
        print(f"[error] failed to handle request: {e}")
    


def consumer_job(args, config, requests_queue: multiprocessing.Queue):
    # Create Consumer instance
    bre_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(bre_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            bre_consumer.assign(partitions)

    # Subscribe to topic
    topic = "dispatcher"
    bre_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = bre_consumer.poll(1.0)
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
        bre_consumer.close()


def start_consumer(args, config, requests_queue):
    global _requests_queue
    _requests_queue = requests_queue
    threading.Thread(target=lambda: consumer_job(args, config, requests_queue)).start()


if __name__ == '__main__':
    start_consumer(None)
