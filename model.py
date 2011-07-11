# -*- coding: utf-8 -*-
import os
# import random
# import urllib
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

def to_json(object):
  u"""オブジェクトをJSONにして返す
  """
  return json.dumps(dict([(attr, getattr(object, attr)) for attr in object._all_properties]))

#
# Model
#
class User(db.Model):
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
    user = cls.all().filter('name =', name).get()
    if not user:
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
