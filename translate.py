#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Copyright (C) 2019 Xvezda <https://xvezda.com/>"""

import os
import re
import json
import time
import functools
import itertools
import requests
from abc import ABCMeta, abstractmethod
from urllib.parse import quote


def roundrobin(*iterables):
  # https://docs.python.org/3/library/itertools.html
  "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
  # Recipe credited to George Sakkis
  num_active = len(iterables)
  nexts = itertools.cycle(iter(it).__next__ for it in iterables)
  while num_active:
    try:
      for next in nexts:
        yield next()
    except StopIteration:
      # Remove the iterator we just exhausted from the cycle.
      num_active -= 1
      nexts = itertools.cycle(itertools.islice(nexts, num_active))


class BaseTranslator(metaclass=ABCMeta):
  def __init__(self):
    pass

  @abstractmethod
  def translate(self, string, src_locale, dst_locale):
    raise NotImplementedError('translate not implemented')


class PapagoTranslator(BaseTranslator):
  API_URL = 'https://openapi.naver.com/v1/papago/n2mt'
  BYTE_LIMIT = 5000
  SUPPORT_LOCALES = [
    ('ko', 'en'), ('ko', 'ja'), ('ko', 'zh-CN'), ('ko', 'zh-TW'),
    ('ko', 'es'), ('ko', 'fr'), ('ko', 'ru'), ('ko', 'vi'),
    ('ko', 'th'), ('ko', 'id'), ('ko', 'de'), ('ko', 'it'),
    ('zh-CN', 'zh-TW'), ('zh-CN', 'ja'), ('zh-TW', 'ja'),
    ('en', 'ja'), ('en', 'zh-CN'), ('en', 'zh-TW'), ('en', 'fr')
  ]

  def __init__(self, client_id='', client_secret=''):
    self._client_id = client_id
    self._client_secret = client_secret
    self._headers = {
      'X-Naver-Client-Id': client_id,
      'X-Naver-Client-Secret': client_secret
    }

  @property
  def client_id(self):
    return self._client_id

  @client_id.setter
  def client_id(self, value):
    headers = self.headers
    headers['X-Naver-Client-Id'] = value
    self.headers = headers
    self._client_id = value

  @property
  def client_secret(self):
    return self._client_secret

  @client_secret.setter
  def client_secret(self, value):
    headers = self.headers
    headers['X-Naver-Client-Secret'] = value
    self.headers = headers
    self._client_secret = value

  @property
  def headers(self):
    return self._headers

  @headers.setter
  def headers(self, value):
    self._headers = value

  def translate(self, string, src_locale, dst_locale):
    if len(string) > self.BYTE_LIMIT:
      raise ValueError('string length should be less than %d' % (self.BYTE_LIMIT))
    if not self.client_id: raise ValueError('client id is not set')
    if not self.client_secret: raise ValueError('client client_secret is not set')

    for pair in self.SUPPORT_LOCALES:
      if src_locale in pair and dst_locale in pair:
        break
    else:
      raise NotImplementedError('locale not supported')
    data = {
      'source': src_locale,
      'target': dst_locale,
      'text': string
    }
    r = requests.post(self.API_URL, headers=self.headers, data=data)
    result = json.loads(r.text)
    return result['message'].get('result')


class GoogleTranslator(BaseTranslator):
  def __init__(self):
    pass


class TranslatorFactory(object):
  def __init__(self):
    pass

  def get_translator(self, name):
    return {'papago': PapagoTranslator, 'google': GoogleTranslator}.get(name)


class MessagesJson(object):
  def __init__(self, filepath):
    self._filepath = filepath
    with open(filepath, 'r') as f:
      self._messages = json.loads(f.read())
    match = re.match(r'(.*)/_locales/(.*?)/messages\.json$', filepath)
    self._path = match.group(1)
    self._locale = match.group(2)

  @property
  def filepath(self):
    return self._filepath

  @filepath.setter
  def filepath(self, value):
    self._filepath = value

  @property
  def messages(self):
    return self._messages

  @messages.setter
  def messages(self, value):
    self._messages = value

  @property
  def path(self):
    return self._path

  @path.setter
  def path(self, value):
    self._path = value

  @property
  def locale(self):
    return self._locale

  @locale.setter
  def locale(self, value):
    self._locale = value


def main_wrapper(main):
  @functools.wraps(main)
  def wrapper_func(*args, **kwargs):
    import sys
    argv = sys.argv
    return main(len(argv), argv)
  return wrapper_func


@main_wrapper
def main(argc, argv):
  self = argv[0]
  items = argv[1:]
  # arr = []
  # for item in items:
  #   arr.append(MessagesJson(item))
  # for item in arr:
  #   print(item.messages)
  factory = TranslatorFactory()
  translator = factory.get_translator('papago')
  papago = translator()
  papago.client_id = os.getenv('NAVER_CLIENT_ID')
  papago.client_secret = os.getenv('NAVER_CLIENT_SECRET')

  result = papago.translate('test', src_locale='en', dst_locale='ko')

  print(result.get('translatedText'))


if __name__ == "__main__":
  main()
