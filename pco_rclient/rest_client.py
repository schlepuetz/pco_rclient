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

DEFAULT_SERVER_INTERFACE = 'xbl-daq-32'
DEFAULT_SERVER_PORT = 9555

FLASK_SERVER_PORT = 9901

# Rest API routes.
ROUTES = {
    "start_pco": "/start_pco_writer",
    "status":"/status",
    "stop": "/stop",
    "kill": "/kill"
}

class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        self.args = "{0.__name__} : {1}".format(type(self), msg),
        if type(msg).__name__ == "ConnectionError":
            print("\n ConnectionError error - it seems that the writer is not running (check ports, configuration file, etc). Please check and try again.\n")
            sys.exit(-1)
        else:
            sys.exit(self)


class PcoError(NoTraceBackWithLineNumber):
    pass


def parse_config_file(full_filename):

    list_args = {}
    for line in open(full_filename):
        fields = line.split()
        if '=' in fields:
            list_args[fields[0]] = fields[-1]
    return list_args

def validate_response_from_writer(writer_response):
    if writer_response['status'] != "receiving":
        print("\nWriter is not receiving. Current status: %s.\n" % writer_response['status'])
    else:
        msg = "\nCurrent status from the writer: %s.\n" % writer_response['status']
        return msg

def validate_response(server_response):
    if not server_response['success']:
         print(server_response['value'])
         quit()
    print("\nPCO Writer configurations successfully submitted to the server... Retrieving writer status...\n")
    sleep(0.5)
    return True


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
    flask_api_address = "http://%s:%s" % (DEFAULT_SERVER_INTERFACE, FLASK_SERVER_PORT)


    if arguments.command == 'stop':
        request_url = api_address + ROUTES["stop"]
        try:
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            raise PcoError(e)
    elif arguments.command == 'status':
        request_url = flask_api_address+ROUTES["status"]
        try:
            response = requests.get(request_url).json()
            msg = "Problem getting status from the writer..."
            if response['success']:
                msg = response['value']
            print(msg)
            sys.exit(0)
        except Exception as e:
            raise PcoError(e)
    elif arguments.command == 'kill':
        request_url = api_address + ROUTES["kill"]
        try:
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            raise PcoError(e)
    elif arguments.command == 'start' and arguments.config:
        args = parse_config_file(arguments.config[0])
        request_url = flask_api_address + ROUTES["start_pco"]
        try:
            response = requests.post(request_url, data=json.dumps(args)).json()
            if validate_response(response):
                # now retrieves status of the writer itself
                request_url = api_address + ROUTES["status"]
                try:
                    response = requests.get(request_url).json()
                    return validate_response_from_writer(response)
                except Exception as e:
                    raise PcoError(e)
        except Exception as e:
            raise PcoError(e)
    else:
        parser.print_help()
        exit(-1)

if __name__ == "__main__":
    # execute only if run as a script
    main()
