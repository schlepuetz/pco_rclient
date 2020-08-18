from pco_controller import PcoWriter
import time
VERBOSE=True
# instantiates one object of the PcoWriter controller
pco_controller = PcoWriter(output_file='./output.h5', 
    dataset_name='data', 
    connection_address="https://129.129.95.47:8080", 
    n_frames=5, 
    user_id=503)

#########################################
# TEST USAGE WHEN WRITER IS NOT RUNNING #
#########################################
# # stop the writer
# pco_controller.stop_writer(VERBOSE)
# # # gets status
# pco_controller.get_status(VERBOSE)
# # # gets stats
# pco_controller.get_statistics(VERBOSE)
# # # kills the writer
# pco_controller.kill_writer(VERBOSE)
# # # getting the configuration
# pco_controller.get_configuration(VERBOSE)
# # # wait the writer
# pco_controller.wait_writer(VERBOSE)
# # # sets config
# pco_controller.set_configuration(output_file='./output_new.h5', 
#     dataset_name='data_black', 
#     connection_address="tcp://pc9808:9999", 
#     n_frames=5,
#     user_id=0,
#     verbose=VERBOSE)

#########
# START #
#########
# start the writer
pco_controller.start_writer(VERBOSE)
time.sleep(3)

# gets status
pco_controller.get_status(VERBOSE)
# gets statistics
pco_controller.get_statistics(VERBOSE)
# sets config
# pco_controller.set_configuration(output_file='./output_new.h5', 
#     dataset_name='data_black', 
#     connection_address="tcp://pc9808:9999", 
#     n_frames=5,
#     user_id=0,
#     verbose=VERBOSE)
# stop the writer
# pco_controller.stop_writer(VERBOSE)
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
pco_controller.wait_writer(VERBOSE)


