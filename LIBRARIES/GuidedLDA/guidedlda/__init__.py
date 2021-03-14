from __future__ import absolute_import, unicode_literals  # noqa

import logging

from LIBRARIES.GuidedLDA.guidedlda.guidedlda import GuidedLDA  # noqa
import LIBRARIES.GuidedLDA.guidedlda.datasets  # noqa

logging.getLogger('guidedlda').addHandler(logging.NullHandler())
