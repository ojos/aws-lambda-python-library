# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import base64
import hashlib
import hmac

INVALID_SIGNATURE = 'INVALID SIGNATURE'

def line_signature(body, key):
    hash = hmac.new(key.encode('utf-8'),
                    body.encode('utf-8'),
                    hashlib.sha256).digest()
    signature = base64.b64encode(hash)
    return signature
