# Copyright (c) 2019 Xvezda <https://xvezda.com/>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from pkg.naver_api import PapagoTranslator
from pkg.google_api import GoogleTranslator


class TranslatorFactory(object):
  def __init__(self):
    pass

  def get_translator(self, name):
    return {'papago': PapagoTranslator, 'google': GoogleTranslator}.get(name)


