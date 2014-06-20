import logging

from google.appengine.api import memcache

from generic import JsonRpcService, TemplatePage

class StartPage(TemplagePage):
  def execute(method, user, request, response, args):
    logging.info("Executing start page")
