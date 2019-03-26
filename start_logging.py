#!/usr/bin/env python
import sys
import curses
import time
import os
import signal
import multiprocessing 


log = ""
start_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())

stdscr = curses.initscr()
curses.noecho()
curses.cbreak()

###############################
###    Interrupt Handler    ###
###############################

def signal_handler(sig, frame):
    finish(0)

signal.signal(signal.SIGINT, signal_handler)

###############################
###    Utility Functions    ###
###############################

def custom_print(inp):
    global log
    log += inp
    stdscr.addstr(inp)
    stdscr.refresh()

def clear_screen():
    stdscr.clear()

def continue_question():
    curses.echo()
    custom_print('Continue? (y/n):')
    while True:
        c = stdscr.getch()
        if c == ord('y') or c == ord('Y'):
            curses.noecho()
            return True
        elif c == ord('n') or c == ord('N'):
            curses.noecho()
            return False
        else:
            custom_print('\nContinue? (y/n):')
    

def finish(t):
    # t is the number of seconds to wait before exiting program
    
    time.sleep(t)
    
    curses.echo()
    curses.nocbreak()
    curses.endwin()


    # Write log
    log_file_name = 'log.txt' #/tmp/logging_'+start_time+'.txt'
    try:
        text_file = open(log_file_name, 'w')
        text_file.write(log)
        text_file.close()
        print('Logs have been written to ' + log_file_name + '.')
    except IOError:
        print('Could not open ' + log_file_name + ' for writing.')

    exit()

################################
###    Use Case Functions    ###
################################

def get_device_list(input_file):

    device_list = []

    try:
        # TODO: Check if file exists and has entries
        with open(input_file, 'r') as filestream:
            
            custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20)) 
            custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('','Username','','Hostname'))
            custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('='*4,'='*20,'='*4,'='*20))  
            
            count = 0

            for line in filestream:
                device_info = line.split(',')
                if len(device_info)!=2:
                    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20)) 
                    custom_print('[ERROR] Malformed input file. Please check line '+str(count+1)+' and try again\n')
                    return None
                count+=1

                device_info = [item.rstrip() for item in device_info]
                # print device_info
                new_device = {}
                new_device['username'] = device_info[0]
                new_device['hostname'] = device_info[1]
                device_list.append(new_device)
                custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('',new_device['username'],'',new_device['hostname']))
            
            custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20))
            
        if len(device_list) == 0:
            custom_print('[ERROR] Empty input file. Please check and try again\n')
            device_list = None

    except IOError:
        custom_print('[ERROR] The input file does not exist.\n')
        device_list = None
    
    return device_list


def check_device(device):
    # TODO: create /data/logs if it doesn't exist. Not too important because it is supposed to be there in new SD cards
    res = os.popen('ssh -q %s@%s.local \'bash -c "\
                            if [ -e /data/logs ]; \
                            then \
                                if [ -e /dev/sda1 ]; \
                                then \
                                    if [ $(mount | grep -c /data/logs) != 1 ]; \
                                    then \
                                        sudo mount -t vfat /dev/sda1 /data/logs -o umask=000 > /dev/null 2>&1; echo Mounted now; \
                                    else \
                                        echo Already Mounted; \
                                    fi; \
                                else \
                                    echo Logs; \
                                fi; \
                            else \
                                echo Nothing; \
                            fi; \
                            "\' || echo Error' %(device['username'],device['hostname'])).read()
    res = res.rstrip()
    return res


def start_logging_checks(device_list):

    pool = multiprocessing.Pool(processes=20)
    results = pool.map(check_device, device_list)
    pool.close()
    pool.join()

    for (res,device) in zip(results, device_list):
        device['preflight_status'] = res.rstrip()

    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20)) 
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('','Device','','Status'))
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('='*4,'='*20,'='*4,'='*20))
    
    for device in device_list:
        custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('',device['hostname'],'',device['preflight_status']))
            
    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20))

    return

def start_device_logging(device):
    res = os.popen('docker -H %s.local run --rm -d --net host --name logger -v /data/logs:/logs \
                        duckietown/rpi-duckiebot-logger:master18 > /dev/null 2>&1;' % (device['hostname'])).read()

    res = os.popen('docker -H %s.local inspect -f \'{{.State.Running}}\' logger' % (device['hostname'])).read()
    res = res.rstrip()
    return res

def start_logging(device_list):
    
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(start_device_logging, device_list)
    pool.close()
    pool.join()

    for (res,device) in zip(results, device_list):
        device['logger_status'] = res.rstrip()

    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20)) 
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('','Device','','Status'))
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('='*4,'='*20,'='*4,'='*20))
    
    for device in device_list:
        custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('',device['hostname'],'',device['logger_status']))
            
    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20))

    return

def stop_device_logging(device):
    res = os.popen('docker -H %s.local stop logger' % (device['hostname'])).read()
    res = res.rstrip()
    return res


def stop_logging(device_list):
    
    pool = multiprocessing.Pool(processes=20)
    results = pool.map(stop_device_logging, device_list)
    pool.close()
    pool.join()

    for (res,device) in zip(results, device_list):
        device['logger_status'] = res.rstrip()

    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20)) 
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('','Device','','Status'))
    custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('='*4,'='*20,'='*4,'='*20))
    
    for device in device_list:
        custom_print('\t|{:<4}{:<20}|{:<4}{:<20}|\n'.format('',device['hostname'],'',device['logger_status']))
            
    custom_print('\t {:<4}{:<20}|{:<4}{:<20} \n'.format('='*4,'='*20,'='*4,'='*20))

    return
    

#########################
###    Main Script    ###
#########################

if __name__ == '__main__':

    device_list = None

    # Step 1
    custom_print('Getting device list:\n')
    device_list = get_device_list('device_list.txt')

    if device_list == None:
        finish(2)

    ret_val = continue_question()
    if not ret_val:
        finish(0)
    else:
        clear_screen()

    # Step 2
    custom_print('Running hardware compliance tests:\n')
    start_logging_checks(device_list)
    
    ret_val = continue_question()
    if not ret_val:
        finish(0)
    else:
        clear_screen()

    # Step 3
    custom_print('Starting logging:\n')
    start_logging(device_list)

    ret_val = continue_question()
    if not ret_val:
        finish(0)
    else:
        clear_screen()

    # Step 3
    custom_print('Stopping logging:\n')
    stop_logging(device_list)

    ret_val = continue_question()
    if not ret_val:
        finish(0)
    else:
        clear_screen()

    custom_print('\nEverything finished successfully. Quack!\n')

    finish(2)
