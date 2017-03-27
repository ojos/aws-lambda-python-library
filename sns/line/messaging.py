# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging

from linebot import HttpClient, LineBotApi, RequestsHttpClient
from linebot.exceptions import LineBotApiError

from ojos.core.decorator import retries, retry_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class Messaging(object):
    _client = None

    def __init__(self, channel_access_token, endpoint=LineBotApi.DEFAULT_API_ENDPOINT,
                 timeout=HttpClient.DEFAULT_TIMEOUT, http_client=RequestsHttpClient):
        self._client = LineBotApi(channel_access_token, endpoint, timeout, http_client)

    @retries(hook=retry_handler)
    def reply_message(self, reply_token, messages, timeout=None):
        self._client.reply_message(reply_token, messages)

    @retries(hook=retry_handler)
    def push_message(self, to, messages, timeout=None):
        if isinstance(to, str):
            self._client.push_message(to, messages)
        elif isinstance(to, list):
            self._client.push_message(to, messages)
