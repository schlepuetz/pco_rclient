
import json
import requests

from requests.exceptions import *

GET  = 'GET'
POST = 'POST'
PUT  = 'PUT'
DELETE = 'DELETE'


class RestClientError(Exception):
    pass


class RestClientHTTPError(RestClientError):

    def __init__(self, response=None):
        if response is not None:
            self.status_code = response.status_code
            self.reason = response.reason
            self.url = response.url
            if response.request:
                self.method = response.request.method
            self.http_message = response.content
        _message = "Rest/HTTP failure: %i %s\nrequest: %s %s\n%s" % (self.status_code, self.reason, self.method, self.url, self.http_message)
        super(RestClientHTTPError, self).__init__(_message)


class RestClient(object):

    def __init__(self, url, timeout=15):
        self._base_url = url
        if not url.endswith("/"):
            self._base_url += "/"

        self._timeout = timeout

        # save latest request/response pair for later inspection, debugging
        self._request = None
        self._response = None


    def get(self, *args, **kwargs):
        return(self.request(GET, *args, **kwargs))

    def post(self, *args, **kwargs):
        return(self.request(POST, *args, **kwargs))

    def put(self, *args, **kwargs):
        return(self.request(PUT, *args, **kwargs))

    def delete(self, *args, **kwargs):
        return(self.request(DELETE, *args, **kwargs))

    def request(self, method, path='', payload=None, query=None):
        """

        query: dictionary, values will form the query string appended to the url, like http://some/where?key1=val1&key2=val2 for
               query = {key1:val1, key2,val2}

        payload: will get converted to json and send as payload or data of the message
        """

        headers={'content-type': 'application/json',
                 'Accept': 'application/json'}
        json_payload = None
        if payload is not None:
            json_payload = json.dumps(payload)

        url = self._base_url + path.lstrip('/')
        try:
            r = requests.request(method=method, url=url, data=json_payload, timeout=self._timeout, headers=headers, params=query)
        except (BaseHTTPError, RequestException) as e:
            # python3 only ;-(   raise RestClientError('rest call %s %s %s failed' % (method, url, payload)) from e
            # catch the exception and raise it again here to get a shorter traceback
            raise e

        self._response = r
        if r.request:
            self._request = r.request
        if r.ok:
            return(self._convert_http_payload_to_python_object(r))
        else:
            raise RestClientHTTPError(r)

    def _convert_http_payload_to_python_object(self, r):
        result = None
        try:
            result = r.json()
        except ValueError:
            result = r.text
        return(result)


