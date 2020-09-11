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
    n_frames=0, 
    max_frames_per_file=5,
    user_id=0,
    debug=DEBUG)

#########################################
# TEST USAGE WHEN WRITER IS NOT RUNNING #
#########################################
# stop the writer
# pco_controller.stop()
# gets status
# pco_controller.get_status()
# gets stats
# pco_controller.get_statistics(VERBOSE)
# kills the writer
# pco_controller.kill()
# getting the configuration
# pco_controller.get_configuration(VERBOSE)
# wait the writer
# pco_controller.wait()
# sets config
# pco_controller.configure(output_file='./output_new.h5', 
#     dataset_name='data_black', 
#     connection_address="tcp://pc9808:9999", 
#     user_id=0,
#     verbose=VERBOSE)
# getting the configuration
# pco_controller.get_configuration(VERBOSE)

# #########
# # START #
# #########
#####################################
# TEST USAGE WHEN WRITER IS RUNNING #
#####################################
# # start the writer
# pco_controller.start(VERBOSE)
# print(pco_controller.status)
# pco_controller.stop(VERBOSE)

# pco_controller.wait(0.1, True)

# time.sleep(5)

# pco_controller.wait()
# time.sleep(5)
# pco_controller.get_status(VERBOSE)
# pco_controller.flush_cam_stream()
# gets status
# pco_controller.wait_writer_verbose()
# pco_controller.get_status(VERBOSE)
# gets statistics
# pco_controller.get_statistics(VERBOSE)
# sets config
# pco_controller.set_configuration(output_file='./output_new.h5', 
#     dataset_name='data_black', 
#     connection_address="tcp://pc9808:9999", 
#     n_frames=5,
#     user_id=0,
#     verbose=VERBOSE)
# stop the writer
# pco_controller.stop(VERBOSE)
# time.sleep(5)
print(pco_controller.get_status_finished())
quit()
# sets config
# pco_controller.set_configuration(output_file='./output_new.h5', 
#     dataset_name='data_white', 
#     connection_address="tcp://pc9808:9999", 
#     n_frames=5,
#     user_id=0,
#     verbose=VERBOSE)
# start the writer
# pco_controller.start_writer(VERBOSE)
# time.sleep(3)
# wait the writer
# pco_controller.wait_writer(VERBOSE)


# pco_controller.stop_writer(VERBOSE)


for file_name in glob.glob(r'/tmp/output*.h5'):
    copy(file_name, "/home/hax_l/software/lib_cpp_h5_writer/tomcat/")
    # os.remove(file_name)


