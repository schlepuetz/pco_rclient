[![CodeFactor](https://www.codefactor.io/repository/github/paulscherrerinstitute/pco_rclient/badge)](https://www.codefactor.io/repository/github/paulscherrerinstitute/pco_rclient) 


# Overview
Rest client script for the pco writer.

# Installation

```bash
conda install -c paulscherrerinstitute pco_rclient
```

# Usage

## pco_controller via python script
The pco_controller is meant for flexible usage and control of the pco writer from within python scripts. 

```python
# Import the client.
from pco_controller import PcoWriter

# Connects to the PcoWriter controller
pco_controller = PcoWriter(output_file='/tmp/output.h5', 
    dataset_name='data', 
    connection_address="https://129.129.95.47:8080", 
    n_frames=5, 
    user_id=503)
# gets status
pco_controller.get_status()
# updates configuration
pco_controller.set_configuration(output_file='/tmp/output_new.h5', 
    dataset_name='data_black', 
    connection_address="https://129.129.95.47:8080", 
    n_frames=10,
    user_id=503)
# gets the configuration
pco_controller.get_configuration()
# starts the writer
pco_controller.start_writer()
# gets statistics
pco_controller.get_statistics()
# wait the writer
pco_controller.wait_writer()
# stop the writer
pco_controller.stop_writer(VERBOSE)
```


## pco_rclient via template files
```bash
usage: pco_rclient [-h] {start,stop,kill,status} ...

Rest api pco writer

optional arguments:
  -h, --help            show this help message and exit

command:
  valid commands

  {start,stop,kill,status}
                        commands
    start               start the writer
    stop                stop the writer
    kill                kill the writer
    status              Retrieve the status of the writer
```

### pco_rclient start
```bash
usage: pco_rclient start [-h] config

positional arguments:
  config      Full path to the configuration file.

optional arguments:
  -h, --help  show this help message and exit
```
Example:
```bash
$ pco_rclient start <path_to_config.pco_file>
```

