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
import feedparser
# from random import choice
# from google.appengine.api import mail

#
# RequestHandler
#
class Index(webapp.RequestHandler):
  def get(self):
    self.response.out.write('hello')


# class PageUser(webapp.RequestHandler):
#   u"""ユーザーデータを扱う
#   """
#   def get(self):
#     u"""ユーザーデータを返す
#     """
#     name = self.request.get('name')
#     user = User.get_user(name)
#     self.response.out.write(user.to_json())


class HtbApi(webapp.RequestHandler):
  u"""Urlテーブルから未取得のurlのはてぶデータを取得して、EntryテーブルとBookmarkテーブルに格納
  """
  def get(self):
    url_list = Url.all().filter('got =', False).fetch(10)

    for url in url_list:
      htb = Entry.get_hatebu_api(url.url)
      url.got = True
      url.put()

      if (htb):
        try:
          entry = Entry.add_entry(htb)
          print "success"
        except:
          print "oops"

class HtbUrl(webapp.RequestHandler):
  u"""パラメタで渡したurlのはてぶデータを取得して、EntryテーブルとBookmarkテーブルに格納
  """
  def get(self):
    rss_list = [
#       'http://feeds.feedburner.com/hatena/b/hotentry',
      'http://b.hatena.ne.jp/hotentry/knowledge.rss',
      'http://b.hatena.ne.jp/hotentry/it.rss',
      'http://b.hatena.ne.jp/hotentry/game.rss',
    ]

    for rss in rss_list:
      f = feedparser.parse(rss)
      for e in f.entries:
        logging.info(e.link)
        url = Url(url = e.link)
        url.put()

class EntryList(webapp.RequestHandler):
  u"""ダンジョン一覧を表示
  """
  def get(self):
    entries = Entry.all().fetch(20)
    path = os.path.join(os.path.dirname(__file__), 'entry_list.html')
    self.response.out.write(template.render(path, {
      'entries': entries
    }))

class Cron(webapp.RequestHandler):
  def get(self):
    pass


# class PageEntryExplore(webapp.RequestHandler):
#   u"""そのページのダンジョンを冒険する
#   """
#   def get(self):
#     name = self.request.get('name')
#     user = User.get_user(name)
#     url = self.request.get('url')
#     entry = Entry.get_entry(url)
#     result = entry.explore(user)
#     self.response.out.write(result)

class PageTest(webapp.RequestHandler):
  u"""テスト用
  """
  def get(self):
    url = self.request.get('url')
    entry = Entry.get_entry(url)
    dir(entry)

application = webapp.WSGIApplication(
    [('/', Index),
#      ('/user', PageUser),
     ('/htb_api', HtbApi),
     ('/htb_url', HtbUrl),
     ('/entry_list', EntryList),
#      ('/admin_entry', PageAdminEntry),
     ('/cron', Cron),
     ('/test', PageTest),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
