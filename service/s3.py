# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import gzip
import logging

try:
    from io import BytesIO
except ImportError:
    from BytesIO import BytesIO

from ojos.core.decorator import retries, retry_handler
from ojos.service.core import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

FALID_GET_OBJECT = 'FAILD GET OBJECT'
FAILD_PUT_OBJECT = 'FAILD PUT OBJECT'
FALID_COPY_OBJECT = 'FAILD COPY'


class S3(object):
    S3_ACL = 'public-read'

    _client = None
    _bucket = None

    def __init__(self, bucket, aws_access_key_id=None, aws_secret_access_key=None,
                 region_name=None):
        self._bucket = bucket
        self._client = client(service_name='s3',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)

    @retries(hook=retry_handler)
    def get_object(self, key):
        return self._client.get_object(Bucket=self._bucket,
                                       Key=key)

    def _expand_text(self, context):
        bytesio = BytesIO(context)
        gzip_file = gzip.GzipFile(fileobj=bytesio, mode='rb')
        context = gzip_file.read()
        gzip_file.close()

        return context

    def _compress_text(self, context):
        bytesio = BytesIO()
        gzip_file = gzip.GzipFile(fileobj=bytesio, mode='wb')
        gzip_file.write(context)
        gzip_file.close()
        context = bytesio.getvalue()

        return context

    @retries(hook=retry_handler)
    def put_object(self, key, body, content_type, cache_control, acl=S3_ACL, compress=False):
        kwargs = {'Bucket': self._bucket,
                  'ACL': acl,
                  'ContentType': content_type,
                  'CacheControl': cache_control,
                  'Key': key,
                  'Body': body}
        if compress:
            kwargs['Body'] = self._compress_text(kwargs['Body'])
            kwargs['ContentEncoding'] = 'gzip'
        return self._client.put_object(**kwargs)

    @retries(hook=retry_handler)
    def copy(self, source_key, target_key):
        self._client.copy(CopySource={'Bucket': self._bucket,
                                      'Key': source_key},
                          Bucket=self._bucket,
                          Key=target_key)
