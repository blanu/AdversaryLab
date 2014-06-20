"""
JSON-RPC module, written to be used with GAE.

tyrion-mx @ chat.freenode.net
"""
import json as parser

class JSONRPCError(Exception):
    """
    A JSONRPCError is an exception that can be sent over the wire, thus can be
    encoded as a json-rpc error response. You should subclass it to implement
    your json-rpc errors, or use it directly.
    """

    def __init__(self, message, code=0, httpStatus=500):
        self.message = message
        self.code = code
        self.httpStatus = httpStatus


class JSONRPC(object):
    """
    This is the main JSONRPC class, and has only one public method.
    You should subclass it, and add some json_{methodName} methods.
    When you call handleRequest with your http json-rpc request data as the
    first argument, the correct json_ method will be automatically executed,
    and the response encoded and returned.
    """

    HTTP_GET = 'GET'
    HTTP_POST = 'POST'

    def handleRequest(self, data, type=HTTP_GET):
        """
        @ivar data: a plain json-rpc request.

        This method will parse the request, execute the requested method if
        present, and return the encoded response.
        Methods should be implemented by subclassing this class and adding one
        or more methods with the suffix json_ (so the request can access only
        secure flagged code). If your method raises an
        Exception it will not be caught, unless it is an instance of
        JSONRPCError. JSONRPCError exceptions will be caught and encoded as an
        error response.

        @returns: an ecoded, ready to be sent, json-rpc response.
        """
        id = 0
        try:
            methodName, params, id = self._decodeRequest(data)

            try:
                method = getattr(self, 'json_%s' % methodName)
            except AttributeError:
                status = 500
                if type == JSONRPC.HTTP_GET:
                    status = 404
                raise JSONRPCError('Procedure Not Found', httpStatus=status)

            result = method(*params)
            error = None
            httpStatus = 200
        except JSONRPCError, e:
            result = None
            error = {'name': e.__class__.__name__,
                     'message': e.message,
                     'code': e.code}
            httpStatus = e.httpStatus

        return self._encodeResponse(result, error, id), httpStatus

    def _decodeRequest(self, data):
        try:
            data = parser.loads(data)
            for var in ('method', 'params', 'id'):
                yield data[var]
        except JSONParseError:
            raise JSONRPCError('Parse Error', httpStatus=500)
        except KeyError:
            raise JSONRPCError('Bad Call', httpStatus=500)

    def _encodeResponse(self, result, error, id):
        response = {'result': result, 'error': error, 'id': id}
        return parser.dumps(response)

