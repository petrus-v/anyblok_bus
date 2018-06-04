# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_bus.validator import bus_validator
from anyblok.column import Integer, String
from marshmallow import Schema, fields
from json import dumps
from anyblok import Declarations
from anyblok_bus.status import MessageStatus
import pika
from anyblok.config import Configuration
from contextlib import contextmanager
from pika.exceptions import ProbableAccessDeniedError, ChannelClosed
pika_url = 'amqp://guest:guest@localhost:5672/%2F'


@contextmanager
def get_channel():
    parameters = pika.URLParameters(pika_url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare('unittest_exchange', durable=True)
    channel.queue_declare('unittest_queue', durable=True)
    channel.queue_purge('unittest_queue')  # case of the queue exist
    channel.queue_bind('unittest_queue', 'unittest_exchange',
                       routing_key='unittest')
    try:
        while True:
            method_frame, header_frame, body = channel.basic_get(
                'unittest_queue')
            if method_frame is None:
                break

        yield channel
    finally:
        if channel and not channel.is_closed and not channel.is_closing:
            channel.close()
        if (
            connection and
            not connection.is_closed and
            not connection.is_closing
        ):
            connection.close()


class OneSchema(Schema):
    label = fields.String(required=True)
    number = fields.Integer(required=True)


class TestPublish(DBTestCase):

    @classmethod
    def init_configuration_manager(cls, **env):
        bus_profile = Configuration.get('bus_profile') or 'unittest'
        env.update(dict(bus_profile=bus_profile))
        super(TestPublish, cls).init_configuration_manager(**env)

    def add_in_registry(self, schema=None):

        @Declarations.register(Declarations.Model)
        class Test:
            id = Integer(primary_key=True)
            label = String()
            number = Integer()

            @bus_validator(name='test', schema=OneSchema())
            def decorated_method(cls, body=None):
                cls.insert(**body)
                return MessageStatus.ACK

    def test_publish_ok(self):
        with get_channel() as channel:
            bus_profile = Configuration.get('bus_profile')
            registry = self.init_registry_with_bloks(('bus',), None)
            registry.Bus.Profile.insert(name=bus_profile, url=pika_url)
            registry.Bus.publish('unittest_exchange', 'unittest',
                                 dumps({'hello': 'world'}),
                                 'application/json')
            method_frame, header_frame, body = channel.basic_get(
                'unittest_queue')
            self.assertIsNotNone(method_frame)

    def test_publish_wrong_url(self):
        bus_profile = Configuration.get('bus_profile')
        registry = self.init_registry_with_bloks(('bus',), None)
        registry.Bus.Profile.insert(
            name=bus_profile,
            url='amqp://guest:guest@localhost:5672/%2Fwrongvhost')
        with self.assertRaises(ProbableAccessDeniedError):
            registry.Bus.publish('unittest_exchange', 'unittest',
                                 dumps({'hello': 'world'}),
                                 'application/json')

    def test_publish_wrong_exchange(self):
        with get_channel() as channel:
            bus_profile = Configuration.get('bus_profile')
            registry = self.init_registry_with_bloks(('bus',), None)
            registry.Bus.Profile.insert(name=bus_profile, url=pika_url)
            with self.assertRaises(ChannelClosed):
                registry.Bus.publish('wrong_exchange', 'unittest',
                                     dumps({'hello': 'world'}),
                                     'application/json')

            method_frame, header_frame, body = channel.basic_get(
                'unittest_queue')
            self.assertIsNone(method_frame)
