# -*- coding: utf-8 -*-

import os
# import pickle
from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import logging
import inspect
from django.utils import simplejson as json
#logging.debug(inspect.currentframe().f_lineno)
from model import *
# from random import choice
# from google.appengine.api import mail

#
# RequestHandler
#
class Index(webapp.RequestHandler):
  def get(self):
    name = self.request.get('name')
    user = User.get_user(name)

    self.response.out.write(to_json(user))

application = webapp.WSGIApplication(
    [('/', Index),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
