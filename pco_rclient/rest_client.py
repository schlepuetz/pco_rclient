#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import argparse
import textwrap
import json
import subprocess
from time import time, sleep
import requests

DEFAULT_SERVER_INTERFACE = 'localhost'
DEFAULT_SERVER_PORT = 5555

# Rest API routes.
ROUTES = {
    "start": "/start",
    "status":"/status",
    "stop": "/stop",
    "kill": "/kill"
}


def parse_config_file(full_filename):
    list_args = []
    for line in open(full_filename):
        fields = line.split()
        if '=' in fields:
            list_args.append(fields[-1])
    return list_args

def validate_response(server_response):
    print(server_response)
    return


def main():

    parser = argparse.ArgumentParser(
        description="Rest api pco writer",
        formatter_class=argparse.RawTextHelpFormatter)

    subparsers = parser.add_subparsers(title='command',
                                       description='valid commands',
                                       dest='command',
                                       help='commands')

    ########
    # CMDS #
    ########
    parser_start = subparsers.add_parser('start',
                                        help='start the writer',
                                        formatter_class=argparse.RawTextHelpFormatter)

    parser_start.add_argument('config', nargs=1, metavar='config',
                             help=textwrap.dedent("Full path to the configuration file."))

    parser_stop = subparsers.add_parser('stop',
                                        help='stop the writer',
                                        formatter_class=argparse.RawTextHelpFormatter)
    parser_kill = subparsers.add_parser('kill',
                                        help='kill the writer',
                                        formatter_class=argparse.RawTextHelpFormatter)
    parser_status = subparsers.add_parser('status',
                                        help='Retrieve the status of the writer',
                                        formatter_class=argparse.RawTextHelpFormatter)

    arguments = parser.parse_args()

    api_address = "http://%s:%s" % (DEFAULT_SERVER_INTERFACE, DEFAULT_SERVER_PORT)



    if arguments.command == 'stop':
        request_url = api_address + ROUTES["stop"]
        try: 
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            print(e)
            quit()
    elif arguments.command == 'status':
        request_url = api_address + ROUTES["status"]
        try: 
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            print(e)
            quit()
    elif arguments.command == 'kill':
        request_url = api_address + ROUTES["kill"]
        try: 
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            print(e)
            quit()
    elif arguments.command == 'start' and arguments.config:
        args = parse_config_file(arguments.config[0])
        # Workaround to use the rest client and run the writer
        p = subprocess.run(parse_config_file(arguments.config[0]))

if __name__ == "__main__":
    # execute only if run as a script
    main()