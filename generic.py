import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from django.utils.simplejson import loads, dumps

from airspeed import CachingFileLoader
from jsonrpc.handler import JSONRPC

class GenericPage(webapp.RequestHandler):
  def options(self, *args):
    self.response.headers['Access-Control-Allow-Origin']='*'
    self.response.headers['Access-Control-Allow-Headers']='Content-Type'
      
  def get(self, *args):
    self.response.headers['Access-Control-Allow-Origin']='*'
    user = users.get_current_user()
    logging.info('Generic user: '+str(user))

    if self.requireLogin() and not user:
      self.redirect(users.create_login_url(self.request.uri))
    else:
      self.execute('get', user, self.request, self.response, args)

  def post(self, *args):
    self.response.headers['Access-Control-Allow-Origin']='*'
    logging.debug('post! '+str(self.request.path)+' '+str(self.__class__))
    user = users.get_current_user()
    self.execute('post', user, self.request, self.response, args)

  def put(self, *args):
    logging.debug('put! '+str(self.request.path)+' '+str(self.__class__))
    user = users.get_current_user()
    self.execute('put', user, self.request, self.response, args)

  def delete(self, *args):
    logging.debug('delete! '+str(self.request.path)+' '+str(self.__class__))
    user = users.get_current_user()
    self.execute('delete', user, self.request, self.response, args)

  def requireLogin(self):
    return False

  def execute(self, method, user, req, resp, args):
    pass

class TemplatePage(GenericPage):
  def execute(self, method, user, req, resp, args):
    logging.info('Template user: '+str(user))
    loader = CachingFileLoader("templates")
    templateName=self.__class__.__name__.lower()
    if templateName[-4:]=='page':
      templateName=templateName[:-4]
    templateName=templateName+".vm"
    template = loader.load_template(templateName)
    context={}
    context['user']=user
    self.processContext(method.upper(), user, req, resp, args, context)
    body=template.merge(context, loader=loader)
#    resp.headers['Content-Type']='text/html'
    resp.out.write(body)

  def processContext(self, method, user, req, resp, args, context):
    pass

class JsonPage(GenericPage):
  def execute(self, method, user, req, resp, args):
    logging.info('JSON user: '+str(user))
    logging.info('req.body: '+str(req.body))
    try:
      obj=loads(req.body)
    except:
      obj=None
    logging.info('obj: '+str(obj))
    output=self.processJson(method.upper(), user, req, resp, args, obj)
#    logging.debug('json output: '+str(output))
    s=dumps(output)
    logging.debug('got output')
    try:
      resp.headers.add_header('content-type', 'application/json')
      resp.out.write(s)
      logging.debug('wrote output '+str(len(s)))
    except Exception, e:
      logging.debug('Failed to write json: '+str(e))

  def processJson(self, method, user, req, resp, args, obj):
    pass

class FilePage(GenericPage):
  def execute(self, method, user, req, resp, args):
    output=self.processFile(method.upper(), user, req, resp, args, req.body)
    if output:
      resp.out.write(output)

  def processFile(self, method, user, req, resp, args, obj):
    pass

class JsonRpcService(webapp.RequestHandler, JSONRPC):
    def post(self):
        response, code = self.handleRequest(self.request.body, self.HTTP_POST)
        self.response.headers['Content-Type'] = 'application/json'
        self.response.set_status(code)
        self.response.out.write(response)
