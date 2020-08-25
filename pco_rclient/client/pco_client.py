# -*- coding: utf-8 -*-
"""Client to control the gigafrost writer
"""

import os
import requests
import json
import pprint
import sys
import time
import itertools

import inspect

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
    "kill": "/kill"
}

class PcoPcoError(Exception):
    pass

class PcoWriter(object):
    """Proxy Class to control the PCO writer
    """
    def __str__(self):
        return("Proxy Class to control the PCO writer. It communicates with "
               "the flask server running on xbl-daq-32 and the writer process "
               "service (pco_writer_1).")

    def __init__(self, output_file='', dataset_name='data', n_frames=0,
                 user_id=503, max_frames_per_file=20000,
                 connection_address='tcp://129.129.99.104:8080',
                 writer_server='xbl-daq-32'):
        self.connection_address = connection_address
        self.flask_api_address = "http://%s:%s" % (writer_server, 9901)
        self.writer_api_address = "http://%s:%s" % (writer_server, 9555)
        if not self.is_running():
            self.output_file = output_file
            self.dataset_name = dataset_name
            self.n_frames = int(n_frames)
            self.max_frames_per_file = int(max_frames_per_file)
            self.user_id = int(user_id)
        else:
            raise RuntimeError("\n Writer configuration can not be updated "
                "while the PCO writer is running. Please, stop() the writer "
                " first and then change the configuration.\n")

        self.configured = self.validate_internal_configuration()

    def set_configuration(self, output_file=None, dataset_name=None,
            n_frames=None, user_id=None, max_frames_per_file=None,
            verbose=False):
        if not self.is_running():
            if output_file is not None:
                self.output_file = output_file
            if dataset_name is not None:
                self.dataset_name = dataset_name
            if n_frames is not None:
                self.n_frames = int(n_frames)
            if user_id is not None:
                self.user_id = int(user_id)
            if max_frames_per_file is not None:
                self.max_frames_per_file = int(max_frames_per_file)
            self.configured = False
            self.configured = self.validate_internal_configuration()
            if verbose:
                print("\nUpdated PCO writer configuration:\n")
                pprint.pprint(self.get_configuration())
                print("\n")
        else:
            if verbose:
                print("\n Writer configuration can not be updated while PCO "
                      "writer is running. Please, stop() the writer to change "
                      "configuration.\n")

    def get_configuration(self, verbose=False):
        if self.configured:
            configuration_dict = {
                "connection_address" : self.connection_address,
                "output_file":self.output_file,
                "n_frames" : str(self.n_frames),
                "user_id" : str(self.user_id),
                "dataset_name" : self.dataset_name,
                "max_frames_per_file" : str(self.max_frames_per_file)
            }
            if verbose:
                print("\nPCO writer configuration:\n")
                pprint.pprint(self.get_configuration())
                print("\n")
            return(configuration_dict)
        else:
            return None

    def start_writer(self, verbose=False):
        """start a new writer process
        """

        if not self.configured:
            raise RuntimeError("please configure the writer by calling the "
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
            self.get_status(verbose=True)

    def wait_writer(self, verbose=False, wait_time=5):
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
        if not self.is_running():
            if verbose:
                print("\nWriter is not running, nothing to wait_writer(). "
                      "Please start it using the start_writer() method.\n")
            return
        spinner = itertools.cycle(['-', '/', '|', '\\'])
        try:
            while self.is_running():
                n_written_frames = self.get_written_frames()
                for _ in range(50):   # ??? Wait_time not used???
                    if verbose:
                        msg = ("Waiting ... Current number of written frames: "
                               "%s %s (Ctrl-C to stop waiting)" %
                               ((str(n_written_frames)),(next(spinner)))
                        sys.stdout.write(msg)
                        sys.stdout.flush()
                        time.sleep(0.1)
                        sys.stdout.write('\r')
                        sys.stdout.flush()
                        if not self.is_running():
                            break
        except KeyboardInterrupt:
            pass
        if verbose :
            if not self.is_running():
                print("\nWriter is not running anymore, exiting "
                      "wait_writer().\n")
            else:
                print("\nWriter is still running, exiting wait_writer().\n")

    def stop_writer(self, verbose=False):
        """Stop the writer
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
            raise PcoError(e)

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
            except Exception as e:
                raise PcoError(e)
        else:
            if verbose:
                print("\nWriter is not running, impossible to "
                      "get_statistics(). Please start it using the "
                      "start_writer() method.\n")

    def get_status(self, verbose=False):
        request_url = self.flask_api_address+ROUTES["status"]
        try:
            response = requests.get(request_url, timeout=3).json()
            if verbose:
                print("\n Writer status: %s \n" % (response['value']))
            return response
        except:
            if verbose:
                print("Problem with the get_status() request.")
            return {'success':True, 'value':'Problem with the status request.'}

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
            return False

    def kill_writer(self, verbose=False):
        # check if writer is running before killing it
        if self.is_running():
            request_url = self.writer_api_address + ROUTES["kill"]
            try:
                response = requests.get(request_url).json()
                if validate_kill_response(response):
                    if verbose:
                        print("\nPCO writer process successfully killed.\n")
                else:
                    print("\nPCO writer kill() failed.")
            except Exception as e:
                raise PcoError(e)
        else:
            if verbose:
                print("\nWriter is not running, impossible to kill(). Please "
                      "start it using the start_writer() method.\n")

    # This does not seem to be used at all???
    #def _clear_configuration(self):
    #    self._configuration = False

    def validate_internal_configuration(self):
        # if self.get_configuration() is not None:
        #     raise RuntimeError('already configured, call reset() if you '
        #                        'want to reconfigure')
        # basic verification if all the parameters are in place
        # if not is_valid_connection_addres(self.connection_address):
        #     raise RuntimeError('Problem with the connection address')
        # if not is_valid_output_file(self.output_file):
        #     raise RuntimeError('Problem with the output_file')
        # if not is_valid_n_frames(self.n_frames):
        #     raise RuntimeError('Problem with the n_frames')
        # if not is_valid_user_id(self.user_id):
        #     raise RuntimeError('Problem with the user_id')
        # if not is_valid_dataset_name(self.dataset_name):
        #     raise RuntimeError('Problem with the dataset_name')
        # if not is_valid_frames_per_file(self.max_frames_per_file):
        #     raise RuntimeError('Problem with the max_frames_per_file')
        return True
