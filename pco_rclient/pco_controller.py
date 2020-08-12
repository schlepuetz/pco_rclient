"""Client to control the gigafrost writer
"""

import os

import requests
import json
import pprint
import sys
import zmq
import threading
from queue import Queue
import time


class NoTraceBackWithLineNumber(Exception):
    def __init__(self, msg):
        self.args = "{0.__name__} : {1}".format(type(self), msg),
        if type(msg).__name__ == "ConnectionError" or  type(msg).__name__ == "ReadTimeout":
            print("\n ConnectionError/ReadTimeout error: it seems that the writer is not running (check server, ports, configuration file, etc). Please check and try again.\n")
        # else:
        #     print("\n Unexpected error: ", msg)

class PcoError(NoTraceBackWithLineNumber):
    pass

def stat_put_routine(socket, q):
    """statistics consumer for pco writer"""
    filter_msg = b'statisticsWriter'
    socket.setsockopt(zmq.SUBSCRIBE, filter_msg)
    while True:
        string  = socket.recv()
        q.put(string)
        

# TODO implementation of validation methods
def is_valid_connection_addres(connection_address):
    return True
def is_valid_output_file(output_file):
    return True
def is_valid_n_frames(n_frames):
    return True
def is_valid_user_id(user_id):
    return True
def is_valid_n_modules(n_modules):
    return True
def is_valid_rest_port(rest_port):
    return True
def is_valid_dataset_name(dataset_name):
    return True
def is_valid_frames_per_file(max_frames_per_file):
    return True
def is_valid_statistics_monitor_address(statistics_monitor_address):
    return True

def validate_response_from_writer(writer_response):
    print("\n\n\n\n writer response", writer_response, "\n\n\n\n")
    if writer_response['status'] != "receiving":
        print("\nWriter is not receiving. Current status: %s.\n" % writer_response['status'])
    else:
        msg = "\nCurrent status from the writer: %s.\n" % writer_response['status']
        return msg

def validate_response(server_response):
    print("\n\n\n\n server response", server_response, "\n\n\n\n")
    if not server_response['success']:
        print(server_response['value'])
        quit()
    print("\nPCO Writer trigger successfully submitted to the server. Retrieving writer's status...\n")
    time.sleep(0.5)
    return True



# Rest API routes.
ROUTES = {
    "start_pco": "/start_pco_writer",
    "status":"/status",
    "stop": "/stop",
    "kill": "/kill"
}

class PcoPcoError(Exception):
    pass

class PcoWriter(object):
    """Proxy Class to control the PCO writer
    """

    def __init__(self, output_file='', dataset_name='data', connection_address='https://129.129.95.47:8080', n_frames=0, 
                user_id=503, n_modules=1, name='pco_writer', rest_api_port=9555, max_frames_per_file=20000, statistics_monitor_address='tcp://*:8088'):

        self.output_file = output_file
        self.dataset_name = dataset_name
        # PCO CONNECTION ADDRESS : INCOMING ZMQ STREAM
        self.connection_address = connection_address
        self.n_frames = n_frames
        self.user_id = user_id
        self.n_modules = n_modules
        self.name = name
        self.rest_api_port = rest_api_port
        self.max_frames_per_file = max_frames_per_file
        self.statistics_monitor_address = statistics_monitor_address
        self.default_args = ['_connection_address', '_output_file', '_n_frames', '_user_id', '_n_modules', '_rest_api_port', '_dataset_name', '_max_frames_per_file', '_statistics_monitor_address']
        self._state = 'initialized'
        # self._flask_api_address = "http://%s:%s" % ('xbl-daq-32', 9555)
        # FLASK SERVER THAT LISTENS AND STARTS THE WRITER PROCESS
        self.flask_api_address = "http://%s:%s" % ('localhost', 9901)
        self.writer_api_address = "http://%s:%s" % ('localhost', self.rest_api_port)
        
        self.configuration = self.validate_internal_configuration()
        
        
        # self.queue = Queue()
        # self.context = zmq.Context()
        # self.socket = self.context.socket(zmq.SUB)
        # self.socket.connect(statistics_monitor_address)
        # self.thread_put = threading.Thread(target=stat_put_routine, args=(self.socket, self.queue))
        

        # self._rest_client = RestClient(url)

    def set_configuration(self, output_file, dataset_name='data', connection_address='https://129.129.95.47:8080', n_frames=0, 
                user_id=503, n_modules=1, name='pco_writer', rest_api_port=9555, max_frames_per_file=20000, statistics_monitor_address='tcp://127.0.0.1:8081'):
        self.output_file = output_file
        self.dataset_name = dataset_name
        self.connection_address = connection_address
        self.n_frames = n_frames
        self.user_id = user_id
        self.n_modules = n_modules
        self.name = name
        self.rest_api_port = rest_api_port
        self.max_frames_per_file = max_frames_per_file
        self.statistics_monitor_address = statistics_monitor_address
        self._state = 'initialized'
        self.configuration = False
        self.configuration = self.validate_internal_configuration()
        pprint.pprint(self.get_configuration())

    def get_configuration(self, verbose=False):
        configuration_dict = {
            "connection_address" : self.connection_address,
            "output_file":self.output_file,
            "n_frames" : str(self.n_frames),
            "user_id" : str(self.user_id),
            "n_modules" : str(self.n_modules),
            "rest_api_port" : str(self.rest_api_port),
            "dataset_name" : self.dataset_name,
            "max_frames_per_file" : str(self.max_frames_per_file),
            "statistics_monitor_address" : self.statistics_monitor_address,
        }
        if verbose:
            pprint.pprint(self.get_configuration())
        return(configuration_dict)

    def start(self, verbose=False):
        """start a new writer process
        """

        if not self.configuration and self.state != 'configured':
            raise RuntimeError('please call set_configuration() before you start()')
        
        request_url = self.flask_api_address + ROUTES["start_pco"]
        try:
            response = requests.post(request_url, data=json.dumps(self.get_configuration())).json()
            if validate_response(response):
                # now retrieves status of the writer itself
                time.sleep(3)
                request_url = self.writer_api_address + ROUTES["status"]
                try:
                    response = requests.get(request_url).json()
                    if validate_response_from_writer(response):
                        self._state = 'running'
                    if verbose:
                        print("\nPCO Writer is running...\n")
                except Exception as e:
                    raise PcoError(e)
        except Exception as e:
            raise PcoError(e)

        if self._state != 'running':
            raise PcoError('start() failed. writer reports %s instead of running' % s)


    def stop(self):
        """stop the writer 
        """

        if self._state == 'stopped': # already closed, nothing to do
            return
        if self._state != 'running':
            raise RuntimeError("writer process isn't running, can't stop()")
        request_url = self.writer_api_address + ROUTES["stop"]
        try:
            response = requests.get(request_url).json()
            return validate_response(response)
        except Exception as e:
            raise PcoError(e)

        if self._state != 'stopped':
            raise PcoError('open() failed. writer reports %s instead of stopped' % s)

    def wait(self):
        # to implement
        return

    def get_stats(self, verbose=False):
        item = self._queue.get()
        print(item)
        return

    def get_status(self,verbose=False):
        request_url = self.flask_api_address+ROUTES["status"]
        try:
            response = requests.get(request_url, timeout=3).json()
            msg = "Problem getting status from the writer..."
            if response['success']:
                msg = response['value']
            print(msg)
        except Exception as e:
            PcoError(e)

    @property
    def state(self):
        configured = self.configuration is not None
        s = (configured, self.state)

        if s == (False, 'absent'):
            state = 'INITIALIZED'
        elif s == (True, 'absent'):
            state = 'CONFIGURED'
        elif s == (True, 'running'):
            state = 'OPEN'
        elif s == (True, 'stopped'):
            state = 'CLOSED'
        else:
            raise RuntimeError('unknown state, something went wrong...')
        return(state)

    def _delete_job_on_writer(self):
        try:
            self._rest_client.delete(self._name)
        except RestClientHTTPError as e:
            if e.status_code != 404:  #don't bother if the job is already gone (404 Resource not found)
                raise

    def _clear_configuration(self):
        self._configuration = False
        # self._thread_put.join()

    def validate_internal_configuration(self):
        # if self.get_configuration() is not None:
        #     raise RuntimeError('already configured, call reset() first if you want to reconfigure ')
        # basic verification if all the parameters are in place
        if not is_valid_connection_addres(self.connection_address):
            raise RuntimeError('Problem with the connection address')
        if not is_valid_output_file(self.output_file):
            raise RuntimeError('Problem with the output_file')
        if not is_valid_n_frames(self.n_frames):
            raise RuntimeError('Problem with the n_frames')
        if not is_valid_user_id(self.user_id):
            raise RuntimeError('Problem with the user_id')
        if not is_valid_n_modules(self.n_modules):
            raise RuntimeError('Problem with the n_modules')
        if not is_valid_rest_port(self.rest_api_port):
            raise RuntimeError('Problem with the rest_api_port')
        if not is_valid_dataset_name(self.dataset_name):
            raise RuntimeError('Problem with the dataset_name')
        if not is_valid_frames_per_file(self.max_frames_per_file):
            raise RuntimeError('Problem with the max_frames_per_file')
        if not is_valid_statistics_monitor_address(self.statistics_monitor_address):
            raise RuntimeError('Problem with the statistics_monitor_address')
        self._state = 'configured'
        return True


