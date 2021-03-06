#!/bin/env python
# -*- coding: UTF-8 -*-

from epics import caput, caget



import sys
import time
import getpass
from datetime import datetime
import os
import inspect
from itertools import ifilter


# inserts the current client's code to path
sys.path.insert(0, '/sls/X02DA/data/e15741/git/pco_rclient/')
from pco_rclient import PcoWriter




def get_datetime_now():
    return datetime.now().strftime("%H%M%S")

###############################
#### SCRIPT USER VARIABLES ####
###############################
# number of frames
nframes = 20
# defines the current time for the uniqueness of the output file
output_str = get_datetime_now()
# verboses 
VERBOSE = True
# user id



if not debug:
    user_id = int(getpass.getuser()[1:])
else:
    user_id = 0
# IOC's name
ioc_name = 'X02DA-CCDCAM2'
#ioc_name = 'X02DA-CCDCAM3'
# Output file path
if not debug:
    outpath = "/sls/X02DA/data/e{}/Data10/pco_test/".format(user_id)
else:
    outpath = '/home/hax_l/software/lib_cpp_h5_writer/tomcat/output/'

if not os.path.isdir(outpath):
    os.makedirs(outpath)

##########################################
#### CAMERA CONFIGURATION AND METHODS ####
##########################################
# IOC COMMANDS
COMMANDS = {
    "CAMERA":       ":CAMERA",
    "FILEFORMAT":   ":FILEFORMAT",
    "RECMODE":      ":RECMODE",
    "STOREMODE":    ":STOREMODE",
    "CLEARMEM":     ":CLEARMEM",
    "SET_PARAM":    ":SET_PARAM",
    "SAVESTOP":     ":SAVESTOP",
    "FTRANSFER":    ":FTRANSFER"
}
# combines the IOCNAME:CMD for a epics command (caput/caget)
def get_caput_cmd(ioc_name, command):
    return str(ioc_name+command)
# starts the camera transfer
def start_cam_transfer(n_frames=nframes):
    caput(get_caput_cmd(ioc_name, COMMANDS["SAVESTOP"]), nframes) # Sets the number of frames to transfer
    caput(get_caput_cmd(ioc_name, COMMANDS["CAMERA"]), 1) # Starts the camera
    time.sleep(1)
    caput(get_caput_cmd(ioc_name, COMMANDS["FTRANSFER"]), 1) # Starts the transfer
# stops the camera transfer
def stop_cam_transfer():
    caput(get_caput_cmd(ioc_name, COMMANDS["CAMERA"]), 0) # Stops the camera
# configures the camera
def config_cam_transfer():
    caput(get_caput_cmd(ioc_name, COMMANDS["CAMERA"]), 0)
    caput(get_caput_cmd(ioc_name, COMMANDS["FILEFORMAT"]), 2)
    caput(get_caput_cmd(ioc_name, COMMANDS["RECMODE"]), 0)
    caput(get_caput_cmd(ioc_name, COMMANDS["STOREMODE"]), 1)
    caput(get_caput_cmd(ioc_name, COMMANDS["CLEARMEM"]), 1)
    caput(get_caput_cmd(ioc_name, COMMANDS["SET_PARAM"]), 1)

# configure the camera
if not debug:
    config_cam_transfer()


###########################
#### PCO CLIENT OBJECT ####
###########################
if not debug:
    pco_controller = PcoWriter(connection_address="tcp://129.129.99.104:8080", 
                           user_id=user_id)
else:
    pco_controller = PcoWriter(connection_address="tcp://129.129.99.104:8080", 
                           user_id=user_id, debug=debug,
                           output_file=os.path.join(outpath, 'test.h5'),
                           n_frames=10, dataset_name='data')


if pco_controller.is_running():
    pco_controller.stop()


problems = 0
ok_flag = True

##############################################
#### TEST METHODS WITH THE RUNNING WRITER ####
##############################################
print('\n\nTesting methods with a running writer - with start()\n\n')
# updates the output_str with the current time
output_str = get_datetime_now()
# runs the writer for an unlimited number of frames
nframes = 20
# configure
print("pco_controller.configure...", end="")
conf_dict = pco_controller.configure(output_file=os.path.join(
    outpath, 'test'+output_str+'.h5'),user_id=user_id,
    dataset_name="data", n_frames=nframes)

# status = configured
if pco_controller.get_status() is not 'configured':
    problems += 1
    ok_flag = False
if ok_flag:
    print(' ✓')
else:
    print(' ⨯')
    ok_flag = True



# start
print("pco_controller.start...", end="")
pco_controller.start()
if pco_controller.get_status() == 'receiving':
    print(' ✓')
else:
    print(' ⨯')

# configure while running -> None
print("pco_controller.configure... (after start)", end="")
ret_configure = pco_controller.configure(output_file=os.path.join(
    outpath, 'test'+output_str+'.h5'),user_id=user_id,
    dataset_name="data", n_frames=nframes)
if ret_configure is not None:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')

# flush_cam_stream while running -> None
print("pco_controller.flush_cam_stream... (after start)", end="")
ret_flush = pco_controller.flush_cam_stream()
if ret_flush is not None:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')

# get_configuration while running
print("pco_controller.get_configuration()... (after start)", end="")
config_dict = pco_controller.get_configuration()
for key in config_dict:
    value = config_dict.get(key, None)
    if value is None:
        problems += 1
        ok_flag = False
if ok_flag:
    print(' ✓')
else:
    print(' ⨯')
    ok_flag = True

# get_server_log while running
print("pco_controller.get_server_log()... (DUMMY LOG - after start)", end="")
count = pco_controller.get_server_log().count('xbl-daq-32.psi.ch')  
if count != 10:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')

print("pco_controller.get_server_uptime()... (DUMMY UPTIME - after start)", end="")
if debug:
    uptime = pco_controller.get_server_uptime().split(" ")
    if uptime[0] != 'active' and uptime[-1] != 'CEST':
        problems += 1
        print(' ⨯')
    else:
        print(' ✓')



print("pco_controller.get_statistics()... (after start)", end="")
statistics_dict = pco_controller.get_statistics()
statistics_ref = {'status': 'receiving', 'success': 'True', 'receiving_rate': 0, 'n_lost_frames': 0, 'n_received_frames': 0, 'start_time': 'Fri Oct  2 15:55:54 2020\n', 'first_frame_id': 0, 'user_id': 0, 'writing_rate': 0, 'end_time': 'Thu Jan  1 00:00:00 1970\n', 'n_written_frames': 0, 'n_frames': 20}
for key in statistics_ref:
    value = statistics_dict.get(key, None)
    if value is None:
        problems += 1
        # print("Problem with %s from get_statistics() method while running..."%key)
        ok_flag = False
if ok_flag:
    print(' ✓')
else:
    print(' ⨯')
    ok_flag = True

# is_connected
print("pco_controller.is_connected()... (after start)", end="")
is_connected = pco_controller.is_connected()
if not is_connected:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')

# is_running
print("pco_controller.is_running()... (after start)", end="")
is_running = pco_controller.is_running()
if not is_running:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')

# get_statistics_writer
print("pco_controller.get_statistics_writer()... (after start)", end="")
statistics_dict = pco_controller.get_statistics_writer()
statistics_ref = {'status': 'receiving', 'success': 'True', 'receiving_rate': 0, 'n_lost_frames': 0, 'n_received_frames': 0, 'start_time': 'Fri Oct  2 15:55:54 2020\n', 'first_frame_id': 0, 'user_id': 0, 'writing_rate': 0, 'end_time': 'Thu Jan  1 00:00:00 1970\n', 'n_written_frames': 0, 'n_frames': 20}
for key in statistics_ref:
    value = statistics_dict.get(key, None)
    if value is None:
        problems += 1
        # print("Problem with %s from get_statistics_writer() method while running..."%key)
        ok_flag = False
if ok_flag:
    print(' ✓')
else:
    print(' ⨯')
    ok_flag = True


# wait
print('pco_controller.wait...')
pco_controller.wait()

# gets status
print('pco_controller.status()... (after start)', end="")
if pco_controller.get_status() not in ['receiving', 'writing']:
    problems += 1
    print("Problem with get_status() method while running...")
    print(' ⨯')
else:
    print(' ✓')
    
# stop
print('pco_controller.stop...', end="")
pco_controller.stop()
if pco_controller.get_status() not in ['finished', 'stopping']:
    problems += 1
    print(' ⨯')
else:
    print(' ✓')


print("pco_controller.get_statistics_last_run()... (after start/stop)", end="")
statistics_dict = pco_controller.get_statistics_last_run()
statistics_ref = {'first_frame_id': '2466', 'user_id': '0', 'n_written_frames': '20', 'n_lost_frames': '0', 'end_time': 'Fri Oct  2 16:38:09 2020\n', 'start_time': 'Fri Oct  2 16:34:51 2020\n', 'n_frames': '20', 'dataset_name': 'data', 'duration_sec': '198.19', 'writing_rate': '0.10091326504869065', 'output_file': '/home/hax_l/software/lib_cpp_h5_writer/tomcat/output/test163451.h5', 'status': 'finished', 'success': True}
if statistics_dict['success'] == False and statistics_dict['status'] is 'unknown':
    problems += 1
    # print("Problem with get_statistics_last_run() after start/stop...")
    ok_flag=False
else:
    for key in statistics_ref:
        value = statistics_dict.get(key, None)
        if value is None:
            problems += 1
            # print("Problem with %s from get_statistics_last_run() after start/stop..."%key)
            ok_flag=False
if ok_flag:
    print(' ✓')
else:
    print(' ⨯')
    ok_flag = True

# gets status
print('pco_controller.status()... (after start/stop)', end="")
if pco_controller.get_status() not in ['finished', 'stopping']:
    problems += 1
    # print("Problem with get_status() after start/stop...")
    print(' ⨯')
else:
    print(' ✓')

# get_status_last_run
print('pco_controller.get_status_last_run()... (after start/stop)', end="")
if pco_controller.get_status_last_run() != 'finished':
    problems += 1
    # print("Problem with get_status_last_run() after start/stop...")
    print(' ⨯')
else:
    print(' ✓')



print("Number of problems: ", problems)
