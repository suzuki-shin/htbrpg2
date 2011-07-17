# -*- coding: utf-8 -*-
import os
# import random
import urllib
#import json
from django.utils import simplejson as json
# import pickle
# from google.appengine.ext.webapp import template
#import cgi
# from google.appengine.api import users
# from google.appengine.ext import webapp
# from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
# import logging
# import inspect
#logging.debug(inspect.currentframe().f_lineno)
from datetime import datetime

#
# Model
#
class SsModel(db.Model):
  u"""モデルクラスの共通の親
  """
  def to_json(self):
    u"""オブジェクトをJSONにして返す
    """
    return json.dumps(dict([(attr, getattr(self, attr)) for attr in self._all_properties]))

#   @classmethod
#   def add_model(cls, prop):
#     u"""データを登録する
#     """
#     model = cls()
#     model.put()

#     return model

class User(SsModel):
  u"""ユーザーキャラクターデータ
  """
  name = db.StringProperty(required=True) #  名前
  lv = db.IntegerProperty(default=1)      #  レベル
  exp = db.IntegerProperty(default=0) #  経験値
#     job = db.IntegerProperty()     #  職種（戦士、魔法使い、ハンター）
  attack = db.IntegerProperty(default=1) #  攻撃力
  magic = db.IntegerProperty(default=1)  #  魔力
  speed = db.IntegerProperty(default=1)  #  スピード

  @classmethod
  def get_user(cls, name):
    u"""ユーザー名からユーザーデータを取得する
    """
    users = cls.all().filter('name =', name).fetch(1)
    print dir(users)
    if users:
      user = users[0]
    else:
      user = cls.add_user(name)
    user.img = str(user.lv) + '.gif' if user.lv <= 25 else '25.gif'

    return user

  @classmethod
  def add_user(cls, name):
    u"""ユーザーデータを登録する
    """
    user = cls(name = name)
    user.put()

    return user


class Entry(SsModel):
  u"""はてぶエントリーページ（ダンジョンと見なす）
  """
  title      = db.TextProperty()  # タイトル
  count      = db.IntegerProperty() # ブックマークしている合計ユーザ数
  url        = db.StringProperty(required=True) # ブックマークされているURL
  entry_url  = db.StringProperty(required=True) # はてなブックマークエントリーページのURL
  screenshot = db.StringProperty()      # スクリーンショット画像のURL
  eid        = db.IntegerProperty()     # エントリーID

  @classmethod
  def get_entry(cls, url):
    u"""urlからエントリデータを取得する
    """
    entries = cls.all().filter('url =', url).fetch(1)
    print dir(entries)
    if entries:
      entry = entries[0]
    else:
      print 'api'
      htb = cls.get_hatebu_api(url)
      entry = cls.add_entry(htb)

    return entry

  @classmethod
  def get_hatebu_api(cls, url):
    api_url = "http://b.hatena.ne.jp/entry/jsonlite/"
    htb_json = urllib.urlopen(api_url + url).read()
    htb = json.loads(htb_json)

    return htb

  @classmethod
  def add_entry(cls, htb):
    u"""エントリデータを登録する
    """
    print htb
    entry = cls(
      title      = htb['title'],
      count      = int(htb['count']),
      url        = htb['url'],
      entry_url  = htb['entry_url'],
      screenshot = htb['screenshot'],
      eid        = int(htb['eid']),
    )
    entry.put()
    Bookmark.add_bookmarks(htb['bookmarks'], entry);

    return entry

  def explore(self, user):
    u"""
    """
    bookmarks = self.get_bookmarks()

    return bookmarks

  def get_bookmarks(self):
    u"""
    """
    return Bookmark.get_bookmarks(self)

class Bookmark(SsModel):
  u"""はてぶエントリーページについてるブックマーク（モンスターとみなす）
  """
  user      = db.StringProperty()       # ブックマークしたユーザ名
  tags      = db.StringListProperty()   # タグの配列
  timestamp = db.DateTimeProperty() # ブックマークした時刻。new Date(timestamp) で JavaScript の Date オブジェクトになります
  comment   = db.StringProperty()   # ブックマークコメント
  entry     = db.ReferenceProperty(Entry) # 所属エントリ

  @classmethod
  def add_bookmarks(cls, bookmarks, entry):
    u"""ブックマークデータを登録する
    """
    for bm in bookmarks:
      timestamp = datetime.strptime(bm['timestamp'], "%Y/%m/%d %H:%M:%S")
      bookmark = cls(
        user      = bm['user'],
        tags      = bm['tags'],
        timestamp = timestamp,
        comment   = bm['comment'],
        entry     = entry,
      )
      bookmark.put()

    return

  @classmethod
  def get_bookmarks(cls, entry):
    u"""指定したエントリにひもづくブックマークデータを取得する
    """
    bookmarks = cls.all().filter('entry =', entry).fetch(100)

    return json.dumps(bookmarks)
