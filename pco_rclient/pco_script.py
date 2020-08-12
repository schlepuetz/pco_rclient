from pco_controller import PcoWriter
import time
VERBOSE=True

# instantiates one object of the PcoWriter controller
pco_controller = PcoWriter('/home/hax_l/software/lib_cpp_h5_writer/tomcat/bin/output.h5', 'data', "tcp://pc9808:9999", 0, 0)
# pco_controller = PcoWriter(connection_address="tcp://pc9808:9999")

# Timeoud while getting status
# pco_controller.get_status(True)

# getting the configuration
# pco_controller.get_configuration(VERBOSE)

# update configuration
# pco_controller.set_configuration('./output_new.h5', 'data_black', "tcp://pc9808:9999", 0)

# start the writer
pco_controller.start(VERBOSE)



time.sleep(15)

# stop the writer
pco_controller.stop()