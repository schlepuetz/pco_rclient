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

# print(pco_controller.is_server_running())
# print(pco_controller.get_server_log())
# pco_controller.get_server_uptime()


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
# quit()
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
# start the writer
# print(pco_controller.get_previous_status())
# print(pco_controller.get_previous_statistics())
# print(pco_controller.get_last_run_stats())
# print(pco_controller.get_status(True))
# print(pco_controller.get_configuration(True))
# print(pco_controller.set_last_configuration())
pco_controller.start(True)
# time.sleep(5)
# print(pco_controller.get_status(VERBOSE))
# print(pco_controller.get_statistics())
# pco_controller.wait(True)
# print(pco_controller.get_statistics())
# pco_controller.wait(True)
# print(pco_controller.get_status())
# # pco_controller.wait(True)
time.sleep(10)
pco_controller.stop(True)
time.sleep(5)
print(pco_controller.get_statistics(True))

# print(pco_controller.get_statistics(True))
# print(pco_controller.get_status(True))

# pco_controller.flush_cam_stream(True)

# time.sleep(5)
# print(pco_controller.get_status())
# print(pco_controller.get_last_run_stats())
# pco_controller.configure(output_file='/tmp/output_new.h5', 
#     dataset_name='data_black', 
#     connection_address="tcp://pc9808:9999", 
#     user_id=0,
#     max_frames_per_file=10,
#     n_frames=6)
# pco_controller.start(VERBOSE)
# pco_controller.wait(True)
# # pco_controller.get_statistics(VERBOSE)
# # print(pco_controller.get_status())
# # pco_controller.wait(0.1, True)

# pco_controller.stop(VERBOSE)
# # time.sleep(5)
# # print(pco_controller.get_last_run_stats())
# # print(pco_controller.get_status())


# # # time.sleep(6)

# # # print(pco_controller.get_last_run_stats())
# # pco_controller.start(VERBOSE)
# # pco_controller.wait(0.1, True)
# # pco_controller.get_statistics(VERBOSE)
# # print(pco_controller.get_status())
# # pco_controller.wait(0.1, True)
# # pco_controller.stop(VERBOSE)
# # time.sleep(5)
# # print(pco_controller.get_last_run_stats())
# # print(pco_controller.get_status())

# # # for file_name in glob.glob(r'/tmp/output*.h5'):
# # #     copy(file_name, "/home/hax_l/software/lib_cpp_h5_writer/tomcat/")
# # #     # os.remove(file_name)


