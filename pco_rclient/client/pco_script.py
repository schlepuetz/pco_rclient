
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
# test scope
test_no_writer = False
test_running_writer = True
# number of frames
nframes = 20
# defines the current time for the uniqueness of the output file
output_str = get_datetime_now()
# verboses 
VERBOSE = True
# user id
user_id = int(getpass.getuser()[1:])
# IOC's name
ioc_name = 'X02DA-CCDCAM2'
#ioc_name = 'X02DA-CCDCAM3'
# Output file path
outpath = "/sls/X02DA/data/e{}/Data10/pco_test/".format(user_id)
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
config_cam_transfer()

###########################
#### PCO CLIENT OBJECT ####
###########################
pco_controller = PcoWriter(connection_address="tcp://129.129.99.104:8080", 
                           user_id=user_id)

##############################################
# TEST METHODS WITHOUT THE RUNNING WRITER ####
##############################################
if test_no_writer:
    print('\n\nTesting methods without the running writer - without start()\n\n')
    time.sleep(2)
    # configure
    print("pco_controller.configure...")
    pco_controller.configure(output_file=os.path.join(
        outpath, 'test'+output_str+'.h5'),
        dataset_name="data", n_frames=nframes)
    # flush_cam_stream
    print('pco_controller.flush_cam_stream')
    start_cam_transfer(nframes)
    pco_controller.flush_cam_stream(timeout=5000, verbose=VERBOSE)
    stop_cam_transfer()
    # get_configuration
    print('pco_controller.get_configuration...')
    pco_controller.get_configuration(verbose=VERBOSE)
    # get_server_log
    print('pco_controller.get_server_log...')
    pco_controller.get_server_log(verbose=VERBOSE)
    # get_server_uptime
    print('pco_controller.get_server_uptime...')
    pco_controller.get_server_uptime(verbose=VERBOSE)
    # get_statistics
    print('pco_controller.get_statistics...')
    pco_controller.get_statistics(verbose=VERBOSE)
    # get_statistics_last_run
    print('pco_controller.get_statistics_last_run...')
    pco_controller.get_statistics_last_run(verbose=VERBOSE)
    # get_statistics_writer
    print('pco_controller.get_statistics_writer')
    pco_controller.get_statistics_writer(verbose=VERBOSE)
    # get_status
    print('pco_controller.get_status')
    pco_controller.get_status(verbose=VERBOSE)
    print(pco_controller.get_status_last_run())
    # get_status_writerstats02DA-CCDCAM2
    print('pco_controller.get_written_frames')
    print(pco_controller.get_written_frames())
    # is_connected
    print('pco_controller.is_connected...')
    print(pco_controller.is_connected())
    # is_running
    print('pco_controller.is_running...')
    print(pco_controller.is_running())
    # kill
    print('pco_controller.kill...')
    pco_controller.kill(verbose=VERBOSE)
    # start
    # pco_controller.start(verbose=VERBOSE)
    # stop
    print('pco_controller.stop...')
    pco_controller.stop(verbose=VERBOSE)
    # wait
    print('pco_controller.wait...')
    pco_controller.wait(verbose=VERBOSE)
    # gets status
    print('pco_controller.status...')
    pco_controller.get_status()

##############################################
#### TEST METHODS WITH THE RUNNING WRITER ####
##############################################
if test_running_writer:
    print('\n\nTesting methods with a running writer - with start()\n\n')
    time.sleep(2)
    # updates the output_str with the current time
    output_str = get_datetime_now()
    # runs the writer for an unlimited number of frames
    nframes = 20
    # configure
    print("pco_controller.configure...")
    pco_controller.configure(output_file=os.path.join(
        outpath, 'test'+output_str+'.h5'),
        dataset_name="data", n_frames=nframes)

    # start
    pco_controller.start(verbose=VERBOSE)
    # is_connected
    print('pco_controller.is_connected...')
    print(pco_controller.is_connected())
    # is_running
    print('pco_controller.is_running...')
    print(pco_controller.is_running())
    # wait
    print('pco_controller.wait...')
    start_cam_transfer(nframes)
    pco_controller.wait()
    stop_cam_transfer()

    # gets status
    print('pco_controller.status...')
    pco_controller.get_status()

    # # get_configuration
    # print('pco_controller.get_configuration...')
    # pco_controller.get_configuration(verbose=VERBOSE)
    # # get_server_log
    # print('pco_controller.get_server_log...')
    # pco_controller.get_server_log(verbose=VERBOSE)
    # # get_server_uptime
    # print('pco_controller.get_server_uptime...')
    # pco_controller.get_server_uptime(verbose=VERBOSE)
    # # get_statistics
    # print('pco_controller.get_statistics...')
    # pco_controller.get_statistics(verbose=VERBOSE)
    # # get_statistics_last_run
    # print('pco_controller.get_statistics_last_run...')
    # pco_controller.get_statistics_last_run(verbose=VERBOSE)
    # # get_statistics_writer
    # print('pco_controller.get_statistics_writer')
    # pco_controller.get_statistics_writer(verbose=VERBOSE)
    # # get_status
    # print('pco_controller.get_status')
    # pco_controller.get_status(verbose=VERBOSE)
    # print(pco_controller.get_status_last_run())
    # # get_status_writerstats02DA-CCDCAM2
    # print('pco_controller.get_written_frames')
    # print(pco_controller.get_written_frames())
    
    # kill
    # print('pco_controller.kill...')
    # pco_controller.kill(verbose=VERBOSE)

    # stop
    # print('pco_controller.stop...')
    # pco_controller.stop(verbose=VERBOSE)

    # stop
    print('pco_controller.stop...')
    pco_controller.stop(verbose=VERBOSE)

# print(w.get_status())
# w.configure(output_file='/sls/X02DA/data/e15741/Data10/disk1/1-10-20/test'+output_str+'.h5',
#     dataset_name="data", n_frames=nframes)
# print(w.get_status())
# print(w.get_configuration())
# w.start()
# time.sleep(5)
# print(w.get_status())

# caput('X02DA-CCDCAM2:SAVESTOP', nframes) # Sets the number of frames to transfer
# caput('X02DA-CCDCAM2:CAMERA', 1) # Starts the camera
# time.sleep(1)
# caput('X02DA-CCDCAM2:FTRANSFER', 1) # Starts the transfer

# w.wait()
# print(w.get_status())
# print(w.get_statistics())

# caput('X02DA-CCDCAM2:CAMERA', 0) # Stops the camera
