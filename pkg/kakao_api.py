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
import json
import requests
from common import BaseTranslator


class KakaoTranslator(BaseTranslator):
  API_URL = 'https://kapi.kakao.com/v1/translation/translate'
  BYTE_LIMIT = 5000
  SUPPORT_LANGS = ["kr", "en", "jp", "cn", "vi", "id", "ar", "bn", "de", "es", "fr", "hi", "it", "ms", "nl", "pt", "ru", "th", "tr"]

  def __init__(self):
    self._api_key = os.getenv('KAKAO_REST_API_KEY')
    self._headers = {
      'Authorization': ('KakaoAK %s' % (self._api_key,))
    }

  @property
  def api_key(self):
    return self._api_key

  @api_key.setter
  def api_key(self, value):
    headers = self.headers
    headers['Authorization'] = 'KakaoAK %s' % (value,)
    self.headers = headers
    self._api_key = value

  @property
  def headers(self):
    return self._headers

  @headers.setter
  def headers(self, value):
    self._headers = value

  def translate(self, string, src_locale, dst_locale):
    src_lang = src_locale.lower()
    target_lang = dst_locale.lower()

    if len(string) > self.BYTE_LIMIT:
      raise ValueError('string length should be less than %d' % (self.BYTE_LIMIT))
    if src_lang == target_lang:
      raise ValueError('source and destination locale should be different')
    if not self.api_key: raise ValueError('api key is not set')

    if not self.is_supported(src_lang, target_lang):
      raise NotImplementedError('language not supported')

    data = {
      'query': string,
      'src_lang': src_lang,
      'target_lang': target_lang,
    }
    r = requests.post(self.API_URL, headers=self.headers, data=data)
    result = json.loads(r.text)
    return '\n'.join(result.get('translated_text')[0])

  def is_supported(self, src_lang, target_lang):
    if src_lang in self.SUPPORT_LANGS and target_lang in self.SUPPORT_LANGS:
      return True
    return False


