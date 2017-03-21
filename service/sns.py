# -*- coding: utf-8 -*-
from __future__ import division, print_function, absolute_import, unicode_literals

import datetime
import json
import logging
import sys
import traceback

from ojos.core.misc import time_from_i
from ojos.service.core import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class SNS(object):
    ERROR_SUBJECT = 'ERROR : %(resource_path)s %(code)s %(message)s'
    ERROR_BODY = '''
timestamp : %(timestamp)s
stage : %(stage)s
resource path : %(resource_path)s
source ip : %(source_ip)s
user agent : %(user_agent)s
trackback : %(trackback)s
request headers : %(headers)s
request body : %(body)s
'''
    MISSED_SUBJECT = 'MISSED : %(code)s %(message)s'
    MISSED_BODY = '''
timestamp : %(timestamp)s
trackback : %(trackback)s
kwargs : %(kwargs)s
'''

    _arn = None

    def __init__(self, arn, aws_access_key_id=None, aws_secret_access_key=None,
                 region_name=None):
        self._arn = arn
        self._client = client(service_name='sns',
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              region_name=region_name)

    def traceback_info(self):
        tbinfo = traceback.format_tb(sys.exc_info()[2])
        return ' '.join(tbinfo).strip()

    def publish(self, subject, message):
        self._client.publish(TargetArn=self._arn,
                             Subject=subject,
                             Message=message)

    def miss(self, code, message, **kwargs):
        jst_dt = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        self.publish(subject=self.MISSED_SUBJECT % {'code': code,
                                                    'message': message},
                     message=self.MISSED_BODY % {'timestamp': jst_dt.strftime('%Y-%m-%dT%H:%M:%S+09:00'),
                                                 'trackback': self.traceback_info(),
                                                 'kwargs': json.dumps(kwargs)})

    def error(self, exception, event):
        response = json.loads(exception.message)
        jst_dt = time_from_i(response['servertime']) + datetime.timedelta(hours=9)
        body = json.dumps(event['body']) if isinstance(event['body'], dict) else event['body']
        self.publish(subject=self.ERROR_SUBJECT % {'resource_path': event['resource_path'],
                                                   'code': response['code'],
                                                   'message': response['message']},
                     message=self.ERROR_BODY % {'timestamp': jst_dt.strftime('%Y-%m-%dT%H:%M:%S+09:00'),
                                                'stage': event['stage'],
                                                'source_ip': event['source_ip'],
                                                'resource_path': event['resource_path'],
                                                'user_agent': event['user_agent'],
                                                'trackback': self.traceback_info(),
                                                'headers': json.dumps(event['headers']),
                                                'body': body})
