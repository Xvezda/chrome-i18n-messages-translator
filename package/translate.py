#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2019 Xvezda <https://xvezda.com/>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

import os
import re
import json
import functools
import itertools
from translator import TranslatorFactory


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

  # factory = TranslatorFactory()
  # translator = factory.get_translator('papago')
  # papago = translator()
  # papago.client_id = os.getenv('NAVER_CLIENT_ID')
  # papago.client_secret = os.getenv('NAVER_CLIENT_SECRET')

  # result = papago.translate('test', src_locale='en', dst_locale='ko')

  # print(result.get('translatedText'))
  factory = TranslatorFactory()
  translator = factory.get_translator('google')
  google = translator()
  print(google._get_supported('en'))


if __name__ == "__main__":
  main()
