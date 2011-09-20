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

class CharaMake(webapp.RequestHandler):
  u"""キャラメイク
  """
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'chara_make.html')
    self.response.out.write(template.render(path, {}))

  def post(self):
    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    chara = Chara(
      user = user,
      name = self.request.get('name'),
      sex = int(self.request.get('sex')),
      job = int(self.request.get('job'))
    )
    chara.put()

    self.response.out.write('hello')

class PartyMake(webapp.RequestHandler):
  u"""パーティメイク
  """
  def post(self):
    logging.info(inspect.currentframe().f_lineno)
    logging.info(self.request.get('party', allow_multiple=True))

    user = users.get_current_user()

    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    party_keys = self.request.get('party', allow_multiple = True)
    logging.info(party_keys)

    if len(party_keys) > 3:
      self.redirect('/')
    elif len(party_keys) == 0:
      self.redirect('/')
    elif len(party_keys) == 1:
      party = Party(user = user)
      party.chara1 = Chara.get(party_keys[0])
    elif len(party_keys) == 2:
      party = Party(user = user)
      party.chara1 = Chara.get(party_keys[0])
      party.chara2 = Chara.get(party_keys[1])
    elif len(party_keys) == 3:
      party = Party(user = user)
      party.chara1 = Chara.get(party_keys[0])
      party.chara2 = Chara.get(party_keys[1])
      party.chara3 = Chara.get(party_keys[2])

    party.put()

    self.response.out.write('hello')

class CharaList(webapp.RequestHandler):
  u"""キャラ一覧
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    chara_list = Chara.all().filter('user =', user).fetch(10)
    path = os.path.join(os.path.dirname(__file__), 'chara_list.html')
    self.response.out.write(template.render(path, {'chara_list': chara_list}))

class PartyList(webapp.RequestHandler):
  u"""パーティー一覧
  """
  def get(self):
    user = users.get_current_user()
    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    party_list = Party.all().filter('user =', user).fetch(10)
    path = os.path.join(os.path.dirname(__file__), 'party_list.html')
    self.response.out.write(template.render(path, {'party_list': party_list}))

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
    self.response.out.write(template.render(path, {'entries': entries}))

class EntryView(webapp.RequestHandler):
  u"""ダンジョン詳細を表示
  """
  def get(self):
    entry = Entry.get(self.request.get('key'))
    path = os.path.join(os.path.dirname(__file__), 'entry_view.html')
    self.response.out.write(template.render(path, {'entry': entry}))

class EntryExplore(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    logging.info(inspect.currentframe().f_lineno)
    if not user:
      self.redirect(users.create_login_url(self.request.uri))

    entry = Entry.get(self.request.get('key'))
    logging.info(entry.url)

    try:
      logging.info(inspect.currentframe().f_lineno)
      entry.explore(user)
    except:
      logging.info(inspect.currentframe().f_lineno)
      self.redirect('/chara_list')

    path = os.path.join(os.path.dirname(__file__), 'explore.html')
    self.response.out.write(template.render(path, {}))

class ExploreDo(webapp.RequestHandler):
  u""" 冒険登録されているデータを実行する。cronでまわす 
  """
  def get(self):
    explores = Explore.all().filter('finished =', False).fetch(10)
    for e in explores:
      e.do()

    self.redirect('/')

class ExploreResultList(webapp.RequestHandler):
  u""" 冒険結果表示
  """
  def get(self):
    user = users.get_current_user()
    explores = Explore.all().filter('user =', user).filter('finished =', True).fetch(10)

    path = os.path.join(os.path.dirname(__file__), 'explore_result_list.html')
    self.response.out.write(template.render(path, {'explores': explores}))

class ExploreResultView(webapp.RequestHandler):
  u""" 冒険結果表示
  """
  def get(self):
    user = users.get_current_user()
    explore = Explore.get(self.request.get('key'))
    battles = explore.get_battles()

    path = os.path.join(os.path.dirname(__file__), 'explore_result_view.html')
    self.response.out.write(template.render(path, {'explore': explore,
                                                   'battles': battles}))

class Cron(webapp.RequestHandler):
  def get(self):
    pass

class PageTest(webapp.RequestHandler):
  u"""テスト用
  """
  def get(self):
    url = self.request.get('url')
    entry = Entry.get_entry(url)
    dir(entry)

application = webapp.WSGIApplication(
    [('/', EntryList),                  # ダンジョンリスト 
#      ('/user', PageUser),
     ('/htb_api', HtbApi),
     ('/htb_url', HtbUrl),
     ('/entry_list', EntryList),        # ダンジョンリスト
     ('/entry_view', EntryView),        # ダンジョン詳細 
     ('/explore', EntryExplore),        # 指定したダンジョンに冒険に出る 
     ('/explore_do', ExploreDo),        # すでに出ている冒険を処理する（cron） 
     ('/explore_result_list', ExploreResultList), # 冒険結果
     ('/explore_result_view', ExploreResultView), # 冒険結果
     ('/chara_make', CharaMake),        # キャラ作成 
     ('/chara_list', CharaList),        # キャラリスト 
     ('/party_make', PartyMake),        # パーティ作成
     ('/cron', Cron),
     ('/test', PageTest),
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

