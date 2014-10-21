"""
This is the web.py file required by App Engine to set up URL paths to handlers.
It defines two URLs, /actions and /views.
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from pages import *
from api import *

app = webapp.WSGIApplication([
  ('/login', Login),
  ('/upload', Upload),
  ('/download', Download),
  ('/downloadReport', DownloadReport),
  ('/uploadReport', UploadReport),
  ('/downloadModel', DownloadModel),

  ('/api/user', UserService),
  ('/api/protocol', ProtocolService),
  ('/api/dataset', DatasetService),
  ('/api/pcap', PcapService),
  ('/api/report', ReportService)
], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
