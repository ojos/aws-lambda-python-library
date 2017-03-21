# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import logging

from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

from ojos.core.decorator import retries, retry_handler
from ojos.service.core import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FALID_INSERT_TO_DYNAMODB = 'FAILD INSERT TO DYNAMODB'
FALID_DELETE_TO_DYNAMODB = 'FAILD DELETE TO DYNAMODB'
FALID_SCAN = 'FAILD SCAN'


class DynamoDB(object):
    _client = None
    _table = None
    _serializer = None
    _deserializer = None

    @property
    def serializer(self):
        if self._serializer is None:
            self._serializer = TypeSerializer()

        return self._serializer

    @property
    def deserializer(self):
        if self._deserializer is None:
            self._deserializer = TypeDeserializer()

        return self._deserializer

    def __init__(self, table, aws_access_key_id=None, aws_secret_access_key=None,
                 region_name=None):
        self._table = table
        self._client = client(service_name='dynamodb',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)

    @retries(hook=retry_handler)
    def put_item(self, item):
        return self._client.put_item(TableName=self._table,
                                     Item=self.serializer.serialize(item)['M'])

    @retries(hook=retry_handler)
    def delete_item(self, key):
        return self._client.delete_item(TableName=self._table,
                                        Key=key)

    @retries(hook=retry_handler)
    def scan(self, last_evaludated_key=None, limit=None):
        kwargs = {'TableName': self._table}
        if last_evaludated_key is not None:
            kwargs['ExclusiveStartKey'] = last_evaludated_key
        if limit is not None:
            kwargs['Limit'] = limit

        res = self._client.scan(**kwargs)
        res['Items'] = [self.deserializer.deserialize({'M': item}) for item in res['Items']]
        return res
