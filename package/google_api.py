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
from common import BaseTranslator
from google.cloud import translate_v3beta1 as translate


class GoogleTranslator(BaseTranslator):
  PROJECT_ID = os.getenv('GOOGLE_PROJECT_ID')
  LOCATION = 'global'
  def __init__(self):
    self._client = translate.TranslationServiceClient()
    self._codes = []

  @property
  def project_id(self):
    return self.PROJECT_ID

  @project_id.setter
  def project_id(self, value):
    self.PROJECT_ID = value

  def translate(self, string, src_locale, dst_locale):
    parent = self._client.location_path(self.PROJECT_ID, self.LOCATION)
    response = self._client.translate_text(
      parent=parent,
      contents=[string],
      mime_type='text/plain',
      source_language_code=src_locale,
      target_language_code=dst_locale)
    return response.translations[0].translated_text

  def is_supported(self, src_locale, dst_locale):
    if not self._codes:
      self._codes = self._get_supported(src_locale)
    codes = self._codes
    if dst_locale not in codes: return False
    return True

  def _get_supported(self, locale):
    parent = self._client.location_path(self.PROJECT_ID, self.LOCATION)
    response = self._client.get_supported_languages(
      parent=parent, display_language_code=locale)
    codes = [language.language_code for language in response.languages]
    return codes


