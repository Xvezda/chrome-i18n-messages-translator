# Copyright (c) 2019 Xvezda <https://xvezda.com/>
#
# Use of this source code is governed by an MIT-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/MIT.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod

class BaseTranslator:
  __metaclass__ = ABCMeta
  def __init__(self):
    pass

  @abstractmethod
  def translate(self, string, src_locale, dst_locale):
    raise NotImplementedError('translate not implemented')

  @abstractmethod
  def is_supported(self, src_locale, dst_locale):
    raise NotImplementedError('translate not implemented')



