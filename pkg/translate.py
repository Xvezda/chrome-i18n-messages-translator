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

import io
import os
import re
import json
import copy
import functools
import itertools
from common import BaseTranslator
from translator import TranslatorFactory


def roundrobin(*iterables):
  # https://docs.python.org/3/library/itertools.html
  "roundrobin('ABC', 'D', 'EF') --> A D E B F C"
  # Recipe credited to George Sakkis
  num_active = len(iterables)
  if hasattr(iter([]), 'next'):
    nexts = itertools.cycle(iter(it).next for it in iterables)
  else:
    nexts = itertools.cycle(iter(it).__next__ for it in iterables)
  while num_active:
    try:
      for next_ in nexts:
        yield next_()
    except StopIteration:
      # Remove the iterator we just exhausted from the cycle.
      num_active -= 1
      nexts = itertools.cycle(itertools.islice(nexts, num_active))


class MessagesJson(object):
  def __init__(self, filepath='', messages={}):
    if filepath: self.filepath = filepath
    if messages: self.messages = copy.deepcopy(messages)

  def __str__(self):
    return json.dumps(self.messages, indent=2, ensure_ascii=False)

  @property
  def filepath(self):
    return self._filepath

  @filepath.setter
  def filepath(self, value):
    try:
      prevpath = self._filepath
    except AttributeError:
      prevpath = None
    self._filepath = value
    if prevpath or not os.path.isfile(value): return
    with io.open(value, 'r', encoding='utf8') as f:
      self.messages = json.loads(f.read(), encoding='utf-8')
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
      os.makedirs(os.path.sep.join(filepath.split(os.path.sep)[:-1]))
    except:
      pass
    with io.open(filepath, 'w', encoding='utf8') as f:
      f.write(self.__str__())


class MessagesHandler(object):
  def __init__(self, messages_json, translated=None):
    if not isinstance(messages_json, MessagesJson):
      raise TypeError('messages is not json type')
    self._messages_json = messages_json
    self._translated = translated

  @property
  def locale(self):
    return self._messages_json.locale

  @property
  def translator(self):
    return self._translator

  @translator.setter
  def translator(self, value):
    if not isinstance(value, BaseTranslator):
      raise TypeError('value is not translator')
    self._translator = value

  def _translate(self, message, to_locale):
    result = self.translator.translate(
      message,
      src_locale=self.locale,
      dst_locale=to_locale
    )
    return result

  def translate(self, target_locales):
    if not self._translator:
      raise ValueError('translator is empty')
    pattern = r'(<code\s?[^>]*?>.+?</code>|</?[^>]+?/?>)'

    for locale in target_locales:
      messages = copy.deepcopy(self._messages_json.messages)
      for key in messages.keys():
        if (self._translated and self._translated[locale]
            and key in self._translated[locale].messages.keys()):
          messages[key]['message'] = \
            self._translated[locale].messages[key]['message']
        else:
          message = messages[key].get('message')
          tokens = re.findall(pattern, message, flags=re.M|re.S)
          if tokens:
            escaped_tokens = map(re.escape, tokens)
            words = re.split('|'.join(escaped_tokens), message)
            translated_words = []
            for word in words:
              if not word.strip():
                result = word
              else:
                result = self.translate(word, to_locale=locale)
              translated_words.append(result)
            if re.match(words[0], message):
              result = roundrobin(translated_words, tokens)
            else:
              result = roundrobin(tokens, translated_words)
            # Reassemble words
            translated = ''.join(list(result))
          else:
            translated = self._translate(message, to_locale=locale)
          messages[key]['message'] = translated
      translated_messages = MessagesJson()
      translated_messages.filepath = self._messages_json.filepath.replace(
        '/'+self.locale+'/messages.json',
        '/'+locale+'/messages.json'
      )
      translated_messages.locale = locale
      translated_messages.messages = messages
      print(translated_messages.filepath)
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
  import collections
  import argparse
  parser = argparse.ArgumentParser()
  parser.add_argument('--pre-translated', '-p',
                      nargs='*',
                      help='Directory path which collect pre-translated '
                           '"messages.json" files located, messages defined '
                           'in this directory will not be translated.')
  parser.add_argument('source', nargs='+')

  args = parser.parse_args()
  if not args.source:
    parser.print_help()
    return 1
  items = args.source

  translated = collections.defaultdict(str)
  if args.pre_translated:
    for pre_translated in args.pre_translated:
      translated_file = MessagesJson(filepath=pre_translated)
      translated[translated_file.locale] = translated_file

  arr = []
  for item in items:
    arr.append(MessagesJson(item))

  factory = TranslatorFactory()
  translator = factory.get_translator('google')
  google = translator()

  # translator = factory.get_translator('papago')
  # papago = translator()

  for messages in arr:
    handler = MessagesHandler(messages, translated=translated)
    handler.translator = google
    # handler.translator = papago
    handler.translate(target_locales=[
      'ko'
      # 'ko', 'ja', 'de', 'zh-CN', 'fr', 'ru'
    ])


if __name__ == "__main__":
  main()
