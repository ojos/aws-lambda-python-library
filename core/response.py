# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging

try:
    import simplejson as json
except ImportError:
    import json

from ojos.core.exception import LambdaException
from ojos.core.misc import now

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _response(code, message, **kwargs):
    response = {'code': code,
                'message': message,
                'servertime': now()}
    response.update(kwargs)
    return response


def success(**kwargs):
    return _response(200, 'OK', **kwargs)


def error(code, message):
    raise LambdaException(json.dumps(_response(code, message)))
