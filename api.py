import logging

from google.appengine.api import memcache

from generic import JsonRpcService
from model import TransactionMonad
from transform import applyAction

from transformUtils import *

from models import View

class StartPage(TemplagePage):
  def execute(method, user, request, response, args):
    logging.info("Executing start page")
