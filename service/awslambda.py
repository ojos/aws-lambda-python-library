# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging
import json
import time

from ojos.core.decorator import retries, retry_handler
from ojos.service.core import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FALID_INVOKE = 'FAILD INVOKE'


class Lambda(object):
    _client = None

    def __init__(self, aws_access_key_id=None, aws_secret_access_key=None,
                 region_name=None, backoff=2):
        self._backoff = backoff
        self._client = client(service_name='lambda',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)

    @retries(hook=retry_handler)
    def invoke(self, function_name, payload, tries=0, invocation_type='Event'):
        if tries > 0:
            time.sleep(self._backoff ** (tries - 1))

        payload['tries'] = tries + 1
        self._client.invoke(FunctionName=function_name,
                            InvocationType=invocation_type,
                            Payload=json.dumps(payload))
