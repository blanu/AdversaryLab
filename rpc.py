"""
The generic module provides the base class from which all API services inherit. It provides a thin interface between App Engine and JSONRPC.
"""

import logging

from google.appengine.ext import webapp

from jsonrpc.handler import JSONRPC

#FIXME - Does not require authentication
class JsonRpcService(webapp.RequestHandler, JSONRPC):
    """ JsonRpcService provides an App Engine request handler which implements the JSON-RPC specification. """
    def get(self):
        response, code = self.handleRequest(self.request.get('jsonrpc'), self.HTTP_GET)

        logging.info('json-rpc request')

        if 'jsonp' in self.request.arguments():
            logging.info('jsonp')
            jsonp=self.request.get('jsonp')
            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.set_status(code)
            self.response.out.write(jsonp+'('+response+')')
        else:
            logging.info('no jsonp')
            # Cross-domain resource sharing
            self.response.headers['Access-Control-Allow-Origin']='*'
            self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
            self.response.headers['Access-Control-Max-Age']='1000'
            self.response.headers['Access-Control-Allow-Headers']='Content-Type'

            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(code)
            self.response.out.write(response)

    def post(self):
        response, code = self.handleRequest(self.request.body, self.HTTP_POST)

        logging.info('json-rpc request: '+str(code))

        if 'jsonp' in self.request.arguments():
            logging.info('jsonp')
            jsonp=self.request.get('jsonp')
            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.set_status(code)
            self.response.out.write(jsonp+'('+response+')')
        else:
            logging.info('no jsonp')
            # Cross-domain resource sharing
            self.response.headers['Access-Control-Allow-Origin']='*'
            self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
            self.response.headers['Access-Control-Max-Age']='1000'
            self.response.headers['Access-Control-Allow-Headers']='Content-Type'

            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(code)
            self.response.out.write(response)

    def options(self):
        # Cross-domain resource sharing
        self.response.headers['Access-Control-Allow-Origin']='*'
        self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
        self.response.headers['Access-Control-Max-Age']='1000'
        self.response.headers['Access-Control-Allow-Headers']='Content-Type'

"""
class PackRpcService(webapp.RequestHandler, PackRPC):
    def get(self):
        response, code = self.handleRequest(self.request.get('pack'), self.HTTP_GET)

        logging.info('pack-rpc request')

        # Cross-domain resource sharing
        self.response.headers['Access-Control-Allow-Origin']='*'
        self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
        self.response.headers['Access-Control-Max-Age']='1000'
        self.response.headers['Access-Control-Allow-Headers']='Content-Type'

        self.response.headers['Content-Type'] = 'application/x-msgpack'
        self.response.set_status(code)
        self.response.out.write(response)

        logging.error('sent rpc response')

    def post(self):
        response, code = self.handleRequest(self.request.body, self.HTTP_POST)

        logging.info('json-rpc request: '+str(code))

        # Cross-domain resource sharing
        self.response.headers['Access-Control-Allow-Origin']='*'
        self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
        self.response.headers['Access-Control-Max-Age']='1000'
        self.response.headers['Access-Control-Allow-Headers']='Content-Type'

        self.response.headers['Content-Type'] = 'application/x-msgpack'
        self.response.set_status(code)
        self.response.out.write(response)

        logging.error('sent rpc response')

    def options(self):
        # Cross-domain resource sharing
        self.response.headers['Access-Control-Allow-Origin']='*'
        self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
        self.response.headers['Access-Control-Max-Age']='1000'
        self.response.headers['Access-Control-Allow-Headers']='Content-Type'

class RestService(webapp.RequestHandler, Rest):
    def get(self, methodName):
        response, code = self.handleRequest(methodName, '{}', self.HTTP_GET)

        logging.info('rest request '+str(methodName)+' '+str(response))

        if 'jsonp' in self.request.arguments():
            logging.info('jsonp')
            jsonp=self.request.get('jsonp')
            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.set_status(code)
            self.response.out.write(jsonp+'('+response+')')
        else:
            logging.info('no jsonp')
            # Cross-domain resource sharing
            self.response.headers['Access-Control-Allow-Origin']='*'
            self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
            self.response.headers['Access-Control-Max-Age']='1000'
            self.response.headers['Access-Control-Allow-Headers']='Content-Type'

            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(code)
            self.response.out.write(response)

    def post(self, methodName):
        response, code = self.handleRequest(methodName, self.request.body, self.HTTP_POST)

        logging.info('rest request: '+str(code))

        if 'jsonp' in self.request.arguments():
            logging.info('jsonp')
            jsonp=self.request.get('jsonp')
            self.response.headers['Content-Type'] = 'text/javascript'
            self.response.set_status(code)
            self.response.out.write(jsonp+'('+response+')')
        else:
            logging.info('no jsonp')
            # Cross-domain resource sharing
            self.response.headers['Access-Control-Allow-Origin']='*'
            self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
            self.response.headers['Access-Control-Max-Age']='1000'
            self.response.headers['Access-Control-Allow-Headers']='Content-Type'

            self.response.headers['Content-Type'] = 'application/json'
            self.response.set_status(code)
            self.response.out.write(response)

    def options(self, methodName):
        # Cross-domain resource sharing
        self.response.headers['Access-Control-Allow-Origin']='*'
        self.response.headers['Access-Control-Allow-Methods']='POST, GET, OPTIONS'
        self.response.headers['Access-Control-Max-Age']='1000'
        self.response.headers['Access-Control-Allow-Headers']='Content-Type'
"""
