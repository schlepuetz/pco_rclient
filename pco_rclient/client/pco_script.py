#!/bin/env python
import time, os
import glob
from shutil import copy
from pco_client import PcoWriter

for file_name in glob.glob(r'/tmp/output*.h5'):
    os.remove(file_name)

VERBOSE=True
DEBUG=True

# instantiates the PcoWriter controller
pco_controller = PcoWriter(output_file='/tmp/output_file.h5', 
    dataset_name='data', 
    connection_address="tcp://pc9808:9999",
    n_frames=10, 
    max_frames_per_file=20,
    user_id=0,
    debug=DEBUG)

#########################################
# TEST USAGE WHEN WRITER IS NOT RUNNING #
#########################################
# configure
pco_controller.configure(output_file='/tmp/output_file_new.h5',
                        dataset_name='data_black',
                        n_frames=15,
                        connection_address='tcp://pc9808:9999',
                        user_id=0,
                        max_frames_per_file=20,
                        verbose=VERBOSE)
# flush_cam_stream
pco_controller.flush_cam_stream(verbose=VERBOSE)
# get_configuration
pco_controller.get_configuration(verbose=VERBOSE)
# get_progress_message
print(pco_controller.get_progress_message())
# get_server_log
pco_controller.get_server_log(verbose=VERBOSE)
# get_server_uptime
pco_controller.get_server_uptime(verbose=VERBOSE)
# get_statistics
pco_controller.get_statistics(verbose=VERBOSE)
# get_statistics_last_run
pco_controller.get_statistics_last_run(verbose=VERBOSE)
# get_statistics_writer
pco_controller.get_statistics_writer(verbose=VERBOSE)
# get_status
pco_controller.get_status(verbose=VERBOSE)
# get_status_last_run
print(pco_controller.get_status_last_run())
# get_status_writer
print(pco_controller.get_status_writer())
# get_written_frames
print(pco_controller.get_written_frames())
# is_connected
print(pco_controller.is_connected())
# is_running
print(pco_controller.is_running())
# kill
pco_controller.kill(verbose=VERBOSE)
# start
# pco_controller.start(verbose=VERBOSE)
# stop
pco_controller.stop(verbose=VERBOSE)
# validate_configuration
print(pco_controller.validate_configuration())
# wait
pco_controller.wait(verbose=VERBOSE)
# gets status
pco_controller.get_status()
# gets stats
pco_controller.get_statistics(VERBOSE)

#####################################
# TEST USAGE WHEN WRITER IS RUNNING #
#####################################
# start
pco_controller.start(verbose=VERBOSE)
# configure
pco_controller.configure(output_file='/tmp/output_file_new.h5',
                        dataset_name='data_black',
                        n_frames=15,
                        connection_address='tcp://pc9808:9999',
                        user_id=0,
                        max_frames_per_file=20,
                        verbose=VERBOSE)
# flush_cam_stream
# pco_controller.flush_cam_stream(verbose=VERBOSE)
# get_configuration
pco_controller.get_configuration(verbose=VERBOSE)
# get_progress_message
print(pco_controller.get_progress_message())
# get_server_log
pco_controller.get_server_log(verbose=VERBOSE)
# get_server_uptime
pco_controller.get_server_uptime(verbose=VERBOSE)
# get_statistics
pco_controller.get_statistics(verbose=VERBOSE)
# get_statistics_last_run
pco_controller.get_statistics_last_run(verbose=VERBOSE)
# get_statistics_writer
pco_controller.get_statistics_writer(verbose=VERBOSE)
# get_status
pco_controller.get_status(verbose=VERBOSE)
# get_status_last_run
print(pco_controller.get_status_last_run())
# get_status_writer
print(pco_controller.get_status_writer())
# get_written_frames
print(pco_controller.get_written_frames())
# is_connected
print(pco_controller.is_connected())
# is_running
print(pco_controller.is_running())
# kill
# pco_controller.kill(verbose=VERBOSE)
# validate_configuration
print(pco_controller.validate_configuration())
# wait
pco_controller.wait(verbose=VERBOSE)
# gets status
pco_controller.get_status()
# stop
pco_controller.stop(verbose=VERBOSE)