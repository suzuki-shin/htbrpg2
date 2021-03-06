# -*- coding: utf-8 -*-
import os
import random
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
import logging
import inspect
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

# class User(SsModel):
#   u"""ユーザーキャラクターデータ
#   """
#   name = db.StringProperty(required=True) #  名前
#   mail = db.EmailProperty()

#   @classmethod
#   def get_user_by_name(cls, name):
#     u"""ユーザー名からユーザーデータを取得する
#     """
#     users = cls.all().filter('name =', name).fetch(1)
#     print dir(users)
#     if users:
#       user = users[0]
#     else:
#       user = cls.add_user(name)
#     user.img = str(user.lv) + '.gif' if user.lv <= 25 else '25.gif'

#     return user

#   @classmethod
#   def get_user_by_mail(cls, name):
#     u"""mailからユーザーデータを取得する
#     """
#     users = cls.all().filter('mail =', mail).fetch(1)
#     print dir(users)
#     if users:
#       user = users[0]
#     else:
#       user = cls.add_user(name)
#     user.img = str(user.lv) + '.gif' if user.lv <= 25 else '25.gif'

#     return user

#   @classmethod
#   def add_user(cls, name):
#     u"""ユーザーデータを登録する
#     """
#     user = cls(name = name)
#     user.put()

#     return user


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
  def get_entry_by_url(cls, url):
    u"""urlからエントリデータを取得する
    """
    entries = cls.all().filter('url =', url).fetch(1)
#     print dir(entries)
    if not entries:
      return None

    return entries[0]

  @classmethod
  def get_entry_by_eid(cls, eid):
    u"""eidからエントリデータを取得する
    """
    entries = cls.all().filter('eid =', eid).fetch(1)
    if not entries:
      return None

    return entries[0]

  @classmethod
  def get_hatebu_api(cls, url):
    u"""はてぶAPI取得
    """
    api_url = "http://b.hatena.ne.jp/entry/jsonlite/"
    htb_json = urllib.urlopen(api_url + url).read()
    htb = json.loads(htb_json)

    return htb

  @classmethod
  def add_entry(cls, htb):
    u"""エントリデータを登録する
    （すでにそのeidが存在したら例外を送出する）
    """
    if cls.get_entry_by_eid(int(htb['eid'])):
      raise "Duplicate Error"

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

  def get_bookmarks(self):
    u"""
    """
    return Bookmark.get_bookmarks(self)

  def explore(self, user):
    u"""冒険にでる
    """
    logging.info(inspect.currentframe().f_lineno)
    party = Party.get_party(user)
    logging.info(party.user)
    explore = Explore(
      user  = user,
      entry = self,
      party = party
    )
    explore.put()

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

    return bookmarks

  def get_power(self):
    return random.randint(1, 6)

class Url(SsModel):
  u"""ダンジョンにするためのurlを入れておく
  """
  url = db.LinkProperty(required=True)
  got = db.BooleanProperty(default=False)
  created_at = db.DateTimeProperty(auto_now_add=True)
  got_at = db.DateTimeProperty()

class Item(SsModel):
  pass

class Weapon(Item):
  pass

class Armor(Item):
  pass

class Accessory(Item):
  pass

class Skill(Item):
  pass

class Chara(SsModel):
  u"""キャラクタ
  """
  user = db.UserProperty(required=True)
  name = db.StringProperty(required=True)
  sex = db.IntegerProperty(required=True)
  age = db.IntegerProperty(default=1, required=True)
  job = db.IntegerProperty(default=1, required=True)
  lv = db.IntegerProperty(default=1, required=True)
  hp = db.IntegerProperty(default=10, required=True)
  attack = db.IntegerProperty(default=1, required=True)
  gurad = db.IntegerProperty(default=1, required=True)
  speed = db.IntegerProperty(default=1, required=True)
  luck = db.IntegerProperty(default=1, required=True)
  weapon = db.ReferenceProperty(Weapon)
  armor = db.ReferenceProperty(Armor)
  accessory = db.ReferenceProperty(Accessory)
  skill1 = db.ReferenceProperty(Skill, None, 'skill1')
  skill2 = db.ReferenceProperty(Skill, None, 'skill2')
  skill3 = db.ReferenceProperty(Skill, None, 'skill3')

class Party(SsModel):
  u"""
  """
  user = db.UserProperty(required=True)
  chara1 = db.ReferenceProperty(Chara, None, 'chara1')
  chara2 = db.ReferenceProperty(Chara, None, 'chara2')
  chara3 = db.ReferenceProperty(Chara, None, 'chara3')

  @classmethod
  def get_party(cls, user):

    logging.info(inspect.currentframe().f_lineno)
    logging.info(user.email)
    logging.info(dir(user))

    parties = cls.all().filter('user =', user).fetch(1)

    logging.info(parties[0].chara1.name)

    if not parties[0]:
      raise "No Party Error"

    return parties[0]

  def get_power(self):
    return random.randint(1, 10)


class Explore(SsModel):
  u"""
  """
  user = db.UserProperty(required=True)
  entry = db.ReferenceProperty(Entry, required=True)
  party = db.ReferenceProperty(Party, required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)
  finished = db.BooleanProperty(required=True, default=False)
  finished_at = db.DateTimeProperty()

  def do(self):
    u"""
    """
    bookmarks = self.entry.get_bookmarks()
    logging.info(bookmarks)
    win = True
    for b in bookmarks:
      battle = self.battle(b)
      win = battle.win
      if not win:
        break

    return win

  def battle(self, bookmark):
    u"""
    """
    p_power = self.party.get_power()
    b_power = bookmark.get_power()
    battle = Battle(
      user           = self.user,
      explore        = self,
      entry          = self.entry,
      party          = self.party,
      bookmark       = bookmark,
      party_power    = p_power,
      bookmark_power = b_power,
      win            = p_power > b_power,
    )
    battle.put()
    self.finished = True
    self.put()

    return battle

  def get_battles(self):
    u"""
    """
    return Battle.all().filter('explore = ', self).fetch(100)

class Battle(SsModel):
  u"""戦闘履歴
  """
  user  = db.UserProperty(required=True)
  explore = db.ReferenceProperty(Explore, required=True)
  entry = db.ReferenceProperty(Entry, required=True)
  party = db.ReferenceProperty(Party, required=True)
  bookmark = db.ReferenceProperty(Bookmark, required=True)
  created_at = db.DateTimeProperty(auto_now_add=True)
  party_power = db.IntegerProperty()
  bookmark_power = db.IntegerProperty()
  win = db.BooleanProperty(required=True)
