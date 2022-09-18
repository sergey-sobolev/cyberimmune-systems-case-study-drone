import time
from producer import proceed_to_deliver


ordering = False
activated = False

def check_operation(id, details):
    global ordering
    global activated
    authorized = False

   # print(f"[info] checking policies for event {id},"\
   #       f" {details['source']}->{details['deliver_to']}: {details['operation']}")
    src = details['source']
    dst = details['deliver_to']
    operation = details['operation']
   
    if not activated:
      if src == 'connector' and dst == 'dispatcher' \
         and operation == 'activate':
            activated = True
            authorized = True    
    else:
        if src == 'connector' and dst == 'monitor' \
            and operation == 'deactivate':
            activated = False
            authorized = True  

    if activated:
        if not ordering:
            if  src == 'connector' and dst == 'dispatcher' \
                and operation == 'task' and len(details) == 12 :
                authorized = True 
        else:
            det = details.copy()
            det['operation'] = 'reject'
            det['deliver_to'] = 'monitor'
            print('rejected')
            proceed_to_deliver(det['id'], det)
            time.sleep(1)
                #todo check content of another fields
        if src == 'dispatcher' and dst == 'position' \
            and operation == 'move_to':
            authorized = True  
        if src == 'dispatcher' and dst == 'position' \
            and operation == 'where_am_i':
            authorized = True    
        if src == 'dispatcher' and dst == 'sprayer' \
            and operation == 'stop':
            authorized = True  
        if src == 'dispatcher' and dst == 'sprayer' \
            and operation == 'start':
            authorized = True    
        if src == 'dispatcher' and dst == 'connector' \
            and operation == 'ask_task':
            authorized = True
        if  src == 'dispatcher' and dst == 'connector'\
            and operation == 'error':
            authorized = True
        if  src == 'dispatcher' and dst == 'position'\
            and operation == 'nonexistent':
            authorized = True
        if  src == 'dispatcher' and dst == 'position'\
            and operation == 'nonexistent2':
            authorized = True
        if  src == 'dispatcher' and dst == 'connector'\
            and operation == 'operation_status':
            authorized = True
            ordering = False

        if  src == 'position' and dst == 'dispatcher'\
            and operation == 'parameters':
            authorized = True
        if  src == 'position' and dst == 'dispatcher'\
            and operation == 'spraying':
            authorized = True
        if  src == 'position' and dst == 'dispatcher'\
            and operation == 'operation_status':
            authorized = True
        if  src == 'position' and dst == 'dispatcher'\
            and operation == 'coordinates':
            authorized = True
            
        if  src == 'recognizer' and dst == 'dispatcher'\
            and operation == 'obstruction':
            authorized = True

    return authorized