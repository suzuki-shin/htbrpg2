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
    self.response.out.write('hello')


class PageUser(webapp.RequestHandler):
  u"""ユーザーデータを扱う
  """
  def get(self):
    u"""ユーザーデータを返す
    """
    name = self.request.get('name')
    user = User.get_user(name)
    self.response.out.write(user.to_json())


class PageEntry(webapp.RequestHandler):
  u"""はてぶデータを扱う
  """
  def get(self):
    url = self.request.get('url')
    entry = Entry.get_entry(url)
    dir(entry)
    self.response.out.write(entry)

class PageEntryExplore(webapp.RequestHandler):
  u"""そのページのダンジョンを冒険する
  """
  def get(self):
    name = self.request.get('name')
    user = User.get_user(name)
    url = self.request.get('url')
    entry = Entry.get_entry(url)
    result = entry.explore(user)
    self.response.out.write(result)

class PageTest(webapp.RequestHandler):
  u"""テスト用
  """
  def get(self):
    url = self.request.get('url')
    entry = Entry.get_entry(url)
    dir(entry)

application = webapp.WSGIApplication(
    [('/', Index),
     ('/user', PageUser),
     ('/entry', PageEntry),
     ('/test', PageTest),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
