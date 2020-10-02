
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


if pco_controller.is_running():
    pco_controller.stop()

##############################################
#### TEST METHODS WITH THE RUNNING WRITER ####
##############################################
print('\n\nTesting methods with a running writer - with start()\n\n')
# updates the output_str with the current time
output_str = get_datetime_now()
# runs the writer for an unlimited number of frames
nframes = 20
# configure
print("pco_controller.configure...")
conf_dict = pco_controller.configure(output_file=os.path.join(
    outpath, 'test'+output_str+'.h5'),user_id=user_id,
    dataset_name="data", n_frames=nframes)
print(conf_dict)
# start
print("pco_controller.start...")
pco_controller.start(verbose=VERBOSE)

# configure after start -> None
print("pco_controller.configure... (after start)")
ret_configure = pco_controller.configure(output_file=os.path.join(
    outpath, 'test'+output_str+'.h5'),user_id=user_id,
    dataset_name="data", n_frames=nframes)
if ret_configure is not None:
    print("Problem with configure()")

# flush after start -> None
print("pco_controller.flush_cam_stream... (after start)")
ret_flush = pco_controller.flush_cam_stream()
if ret_flush is not None:
    print("Problem with flush_cam_stream()...")

# get_configuration after start
config_dict = pco_controller.get_configuration()
for key in config_dict:
    value = config_dict.get(key, None)
    if value is None:
        print("Problem with %s from get_configuration() method..."%key)

# is_connected
is_connected = pco_controller.is_connected()
if not is_connected:
    print("Not connected after the start...")
# is_running
is_running = pco_controller.is_running()
if not is_running:
    print("Not running after the start...")
# wait
print('pco_controller.wait...')
start_cam_transfer(nframes)
pco_controller.wait()
stop_cam_transfer()

# gets status
print('pco_controller.status...')
pco_controller.get_status()
# stop
print('pco_controller.stop...')
pco_controller.stop(verbose=VERBOSE)
