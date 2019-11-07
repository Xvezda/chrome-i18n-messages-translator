#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Xvezda <https://xvezda.com/>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import json
import functools
import itertools
from common import BaseTranslator
from translator import TranslatorFactory


def roundrobin(*iterables):
  # https://docs.python.org/3/library/itertools.html
  "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
  # Recipe credited to George Sakkis
  num_active = len(iterables)
  nexts = itertools.cycle(iter(it).next for it in iterables)
  while num_active:
    try:
      for _next in nexts:
        yield _next()
    except StopIteration:
      # Remove the iterator we just exhausted from the cycle.
      num_active -= 1
      nexts = itertools.cycle(itertools.islice(nexts, num_active))


class MessagesJson(object):
  def __init__(self, filepath='', messages={}):
    if filepath: self.filepath = filepath
    if messages: self.messages = messages

  def __str__(self):
    return json.dumps(self.messages, indent=2)

  @property
  def filepath(self):
    return self._filepath

  @filepath.setter
  def filepath(self, value):
    self._filepath = value
    if not os.path.isfile(value): return
    with open(value, 'r') as f:
      self.messages = json.loads(f.read())
    match = re.match(r'(.*)/_locales/(.*?)/messages\.json$', value)
    self.path = match.group(1)
    self.locale = match.group(2)

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

  def write(self):
    filepath = self.filepath
    if not filepath:
      raise ValueError('filepath is empty')
    try:
      os.makedirs('/'.join(filepath.split('/')[:-1]))
    except:
      pass
    with open(filepath, 'w') as f:
      f.write(self.__str__())


class MessagesHandler(object):
  def __init__(self, messages_json):
    if not isinstance(messages_json, MessagesJson):
      raise TypeError('messages is not json type')
    self._messages_json = messages_json
    self._translated = []

  @property
  def translator(self):
    return self._translator

  @translator.setter
  def translator(self, value):
    if not isinstance(value, BaseTranslator):
      raise TypeError('value is not translator')
    self._translator = value

  def translate(self, target_locales):
    if not self._translator:
      raise ValueError('translator is empty')
    pattern = r'(<code\s?[^>]*?>.*?</code>|</?[^>]*?/?>)'
    messages = self._messages_json.messages
    src_locale = self._messages_json.locale
    # print('messages:', messages)
    for locale in target_locales:
      for key in messages:
        message = messages[key].get('message')
        tokens = re.findall(pattern, message, flags=re.M|re.S)
        escaped_tokens = map(re.escape, tokens)
        words = re.split('|'.join(escaped_tokens), message)
        translated_words = []
        # print('tokens:', tokens)
        # print('words:', words)
        for word in words:
          if not word.strip():
            result = word
          else:
            assert src_locale != locale
            result = self.translator.translate(
              word,
              src_locale=src_locale,
              dst_locale=locale
            )
          translated_words.append(result)
        if re.match(words[0], message):
          result = roundrobin(translated_words, tokens)
        else:
          result = roundrobin(tokens, translated_words)
        translated = ''.join(list(result))
        # print('result:', translated)
        messages[key]['message'] = translated
        # messages[key]['message'] = 'test'
      translated_messages = MessagesJson(messages=messages)
      translated_messages.filepath = self._messages_json.filepath.replace(
        '/'+src_locale+'/messages.json',
        '/'+locale+'/messages.json'
      )
      translated_messages.locale = locale
      print(translated_messages.filepath)
      print(translated_messages)
      translated_messages.write()


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
  arr = []
  for item in items:
    arr.append(MessagesJson(item))

  factory = TranslatorFactory()
  translator = factory.get_translator('google')
  google = translator()

  # translator = factory.get_translator('papago')
  # papago = translator()

  for messages in arr:
    handler = MessagesHandler(messages)
    handler.translator = google
    handler.translate(target_locales=[
      'ko', 'ja', 'de', 'zh-CN', 'fr', 'ru'
    ])


if __name__ == "__main__":
  main()
