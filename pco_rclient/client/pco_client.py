# -*- coding: utf-8 -*-
"""Client to control the gigafrost writer
"""

import os
import requests
import re
import json
import pprint
import sys
import time
import itertools
import zmq
import inspect
from enum import Enum

class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        if (type(msg).__name__ == "ConnectionError" or
            type(msg).__name__ == "ReadTimeout"):
            print("\n ConnectionError/ReadTimeout: it seems that the server "
                  "is not running (check xbl-daq-32 pco writer service "
                  "(pco_writer_1), ports, etc).\n")
        try:
            ln = sys.exc_info()[-1].tb_lineno
        except AttributeError:
            ln = inspect.currentframe().f_back.f_lineno
        self.args = "{0.__name__} (line {1}): {2}".format(type(self), ln, msg),
        sys.tracebacklimit = None
        return None

class PcoError(NoTraceBackWithLineNumber):
    pass

class PcoWarning(NoTraceBackWithLineNumber):
    pass

# TODO implementation of proper validation tests
def is_valid_connection_addres(connection_address):
    return True
def is_valid_output_file(output_file):
    return True
def is_valid_n_frames(n_frames):
    return True
def is_valid_user_id(user_id):
    return True
def is_valid_rest_port(rest_port):
    return True
def is_valid_dataset_name(dataset_name):
    return True
def is_valid_frames_per_file(max_frames_per_file):
    return True

def insert_placeholder(string, index):
    return string[:index] + "%03d" + string[index:]

def validate_statistics_response(writer_response, verbose=False):
    return writer_response

def validate_response(server_response, verbose=False):
    if not server_response['success']:
        print(server_response['value'])
        return False
    return True

def validate_kill_response(writer_response, verbose=False):
    if writer_response['status'] == "killed":
        if verbose:
            print(writer_response['status'])
        return True
    else:
        return False

# Rest API routes.
ROUTES = {
    "start_pco": "/start_pco_writer",
    "status":"/status",
    "statistics":"/statistics",
    "stop": "/stop",
    "kill": "/kill",
    "finished": "/finished"
}


# class StatusEnum(Enum):
#     INITIALIZED = 0
#     ERROR = 1
#     RECEIVING = 2
#     WRITING = 3
#     FINISHED = 4


class PcoPcoError(Exception):
    pass

class PcoWriter(object):
    """Proxy Class to control the PCO writer
    """
    def __str__(self):
        return("Proxy Class to control the PCO writer. It communicates with "
               "the flask server running on xbl-daq-32 and the writer process "
               "service (pco_writer_1).")

    def __init__(self, output_file='', dataset_name='data', 
                connection_address='tcp://129.129.99.104:8080', n_frames=0,
                user_id=503, max_frames_per_file=20000, debug=False):
        self.connection_address = connection_address
        self.flask_api_address = "http://%s:%s" % ('xbl-daq-32', 9901)
        self.writer_api_address = "http://%s:%s" % ('xbl-daq-32', 9555)
        self.status = 'initialized'
        if not debug:
            is_writer_running = self.is_running()
            if not is_writer_running:
                self.output_file = output_file
                self.dataset_name = dataset_name
                if isinstance(n_frames, int):
                    self.n_frames = n_frames
                if isinstance(max_frames_per_file, int):
                    self.max_frames_per_file = max_frames_per_file
                if isinstance(user_id, int):
                    self.user_id = user_id        
            else:
                raise RuntimeError("\n Writer configuration can not be updated "
                    "while the PCO writer is running. Please, stop() the writer "
                    " first and then change the configuration.\n")
        else:
            print("\nSetting debug configurations... \n")
            self.flask_api_address = "http://localhost:9901"
            self.writer_api_address = "http://localhost:9555"
            self.connection_address = "tcp://pc9808:9999"
            self.output_file = output_file
            self.user_id = 0
            self.n_frames = n_frames
            self.dataset_name = dataset_name
            self.max_frames_per_file = max_frames_per_file
        if self.max_frames_per_file != 20000:
            # if needed, it verifies if output_file has placeholder
            regexp = re.compile(r'%[\d]+d')
            if not regexp.search(self.output_file):
                self.output_file = insert_placeholder(self.output_file, len(self.output_file)-3)

    def configure(self, output_file=None, dataset_name=None, n_frames=None, connection_address=None,
                user_id=None, max_frames_per_file=None, verbose=False):
        is_writer_running = self.is_running()
        if not is_writer_running:
            if output_file is not None:
                self.output_file = output_file
            if dataset_name is not None:
                self.dataset_name = dataset_name
            if int(n_frames) and n_frames is not None:
                self.n_frames = n_frames
            if int(user_id) and user_id is not None:
                self.user_id = user_id
            if int(max_frames_per_file) and max_frames_per_file is not None:
                self.max_frames_per_file = max_frames_per_file
            if connection_address is not None:
                self.connection_address = connection_address
            if verbose:
                print("\nUpdated PCO writer configuration:\n")
                pprint.pprint(self.get_configuration())
                print("\n")
        else:
            if verbose:
                print("\n Writer configuration can not be updated while PCO "
                      "writer is running. Please, stop() the writer to change "
                      "configuration.\n")
        self.status = 'initialized'
       

    def get_configuration(self, verbose=False):
        if self.status =='initialized':
            configuration_dict = {
                "connection_address" : self.connection_address,
                "output_file":self.output_file,
                "n_frames" : str(self.n_frames),
                "user_id" : str(self.user_id),
                "dataset_name" : self.dataset_name,
                "max_frames_per_file" : str(self.max_frames_per_file),
                "statistics_monitor_address": "tcp://*:8088",
                "rest_api_port": "9555",
                "n_modules": "1"
            }
            if verbose:
                print("\nPCO writer configuration:\n")
                pprint.pprint(configuration_dict)
                print("\n")
        else:
            return None
        
        return(configuration_dict)

    def start(self, verbose=False):
        """start a new writer process
        """
        if self.status != 'initialized':
            raise PcoError("please configure the writer by calling the "
                "set_configuration() command before you start_writer()")
        
        # check if writer is running before starting it
        if not self.is_running():
            request_url = self.flask_api_address + ROUTES["start_pco"]
            try:
                response = requests.post(request_url,
                    data=json.dumps(self.get_configuration())).json()
                if validate_response(response):
                    if verbose:
                        #giving some time before returning to the cli - why?
                        time.sleep(1)
                        print("\nPCO writer trigger start successfully "
                              "submitted to the server.\n")
                else:
                    print("\nPCO writer trigger start failed. "
                          "Server response: %s\n" % (response))
            except Exception as e:
                raise PcoWarning(e)
        else:
            print("\nWriter is already running, impossible to start_writer() "
                  "again. Getting the status of the writer... \n")
            self.get_status()

    def wait(self, wait_time=5, verbose=False):
        """Wait for the writer to finish the writing process.
        """
        

        # TODO: correctly implement the wait_time
        #       A global timeout is probably not a good idea since it is very
        #       difficult to predict in a simple way how long the writer will
        #       be busy to write a given data stream. It's probably better to
        #       check if the number of written frames keeps chaning (meaning
        #       the writer is working), and if that is not the case for a given
        #       maximum duration of inactivity, then the wait process times
        #       out.

        # check if writer is running before killing it
        is_writer_running = self.is_running()
        if not is_writer_running:
            print("\nWriter is not running, nothing to wait().\n")
            return
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        try:
            while is_writer_running:
                if not is_writer_running:
                    break
                else:
                    n_written_frames = self.get_written_frames()
                for _ in range(50):
                    msg = "Writer is running ... Current number of written frames: %s %s (Ctrl-C to stop waiting)" % ((str(n_written_frames)),(next(spinner)))
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                    time.sleep(wait_time)
                    sys.stdout.write('\r')
                    sys.stdout.flush()
                is_writer_running = self.is_running()
        except KeyboardInterrupt:
            pass
        if not is_writer_running and verbose:
            print("\nWriter is not running anymore, exiting wait().\n")
        elif verbose:
            print("\nWriter is still running, exiting wait().\n")
        

    def flush_cam_stream(self, verbose=False):
        if verbose:
            print("Flushing camera stream ... (Ctrl-C to stop)")
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.connect(self.connection_address)
        x = 0
        consumer = True
        while consumer:
            string = socket.recv()
            if x % 2 != 1:
                try:
                    d = json.loads(string.decode())
                    if verbose:
                        print(d)
                except KeyboardInterrupt:
                    consumer = False
                    raise PcoError(e)
            x+=1
        return

    def stop(self, verbose=False):
        """stop the writer 
        """
        # check if writer is running before killing it
        if self.is_running():
            request_url = self.writer_api_address + ROUTES["stop"]
            try:
                response = requests.get(request_url).json()
                if validate_response(response):
                    if verbose:
                        print("\nPCO writer trigger stop successfully "
                              "submitted to the server.\n")
                else:
                    print("\nPCO writer stop writer failed. Server response: "
                          "%s\n" % (response))
            except Exception as e:
                raise PcoError(e)
        else:
            if verbose:
                print("\nWriter is not running, impossible to stop_writer(). "
                      "Please start it using the start_writer() method.\n")

    def get_written_frames(self):
        request_url = self.writer_api_address + ROUTES["statistics"]
        try:
            response = requests.get(request_url).json()
            if validate_statistics_response(response):
                return response['n_written_frames']
        except Exception as e:
            return None


    def get_statistics(self, verbose=False):
        # check if writer is running before getting statistics
        is_writer_running = self.is_running()
        if is_writer_running:
            request_url = self.writer_api_address + ROUTES["statistics"]
            try:
                response = requests.get(request_url).json()
                if validate_statistics_response(response):
                    if verbose:
                        print("\nPCO writer statistics:\n")
                        pprint.pprint(response)
                        print("\n")
                    return response
            except Exception as e:
                raise PcoError(e)
        else:
            if verbose:
                print("\nWriter is not running, impossible to "
                      "get_statistics(). Please start it using the "
                      "start_writer() method.\n")
            
    def get_status_finished(self):
        request_url = self.flask_api_address+ROUTES["finished"]
        try:
            response = requests.get(request_url, timeout=3).json()
            self.status = response['value']
            return self.status
        except:
            self.status = 'error'
            return self.status
                

    def get_status(self, verbose=False):
        request_url = self.flask_api_address+ROUTES["status"]
        try:
            response = requests.get(request_url, timeout=3).json()
            self.status = response['value']
            return self.status
        except:
            self.status = 'error'
            return self.status

    def is_running(self):
        request_url = self.flask_api_address+ROUTES["status"]
        try:
            response = requests.get(request_url, timeout=3).json()
            if (response['value'] == 'receiving' or
                response['value'] == 'writing'):
                return True
            else:
                return False
        except:
            self.status = 'error'
            return False

    def kill(self, verbose=False):
        # check if writer is running before killing it
        if self.is_running():
            request_url = self.writer_api_address + ROUTES["kill"]
            try:
                response = requests.get(request_url).json()
                if validate_kill_response(response):
                    if verbose:
                        print("\nPCO writer process successfully killed.\n")
                    self.status = 'finished'
                else:
                    print("\nPCO writer kill() failed.")
            except Exception as e:
                raise PcoError(e)
        else:
            if verbose:
                print("\nWriter is not running, impossible to kill(). Please "
                      "start it using the start_writer() method.\n")
