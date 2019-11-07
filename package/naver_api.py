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
    self._client_id = client_id or os.getenv('NAVER_CLIENT_ID')
    self._client_secret = client_secret or os.getenv('NAVER_CLIENT_SECRET')
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
    if src_locale == dst_locale:
      raise ValueError('source and destination locale should be different')
    if not self.client_id: raise ValueError('client id is not set')
    if not self.client_secret: raise ValueError('client client_secret is not set')

    if not self.is_supported(src_locale, dst_locale):
      raise NotImplementedError('locale not supported')

    data = {
      'source': src_locale,
      'target': dst_locale,
      'text': string
    }
    r = requests.post(self.API_URL, headers=self.headers, data=data)
    result = json.loads(r.text)
    if result.get('errorCode'):
      raise Exception(result.get('errorMessage'))
    return result.get('message').get('result').get('translatedText')

  def is_supported(self, src_locale, dst_locale):
    for pair in self.SUPPORT_LOCALES:
      if src_locale in pair and dst_locale in pair:
        return True
    else:
      return False


