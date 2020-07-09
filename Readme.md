
# Overview
Rest client script for the pco writer.

# Installation

```bash
conda install -c paulscherrerinstitute pco_rclient
```

# Usage

## pco_rclient
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

