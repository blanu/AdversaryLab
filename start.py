import logging
import subprocess

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

from generic import GenericPage

class Start(GenericPage):
  def execute(self, method, user, req, resp, args):
    logging.info('Start')
#    subprocess.call(['sudo', 'pip', 'install', 'cython'])
#    subprocess.call(['sudo', 'pip', 'install', 'numpy'])
#    subprocess.call(['sudo', 'pip', 'install', 'pystan'])

app = webapp.WSGIApplication([
  ('/_ah/start', Start),
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
