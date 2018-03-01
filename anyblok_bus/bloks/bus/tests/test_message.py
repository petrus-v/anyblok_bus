# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import BlokTestCase
from base64 import b64encode
from testfixtures import LogCapture
import mock


class TestMessage(BlokTestCase):

    def setUp(self):
        self.test_message = b64encode(b'test message')
        self.profile_model = self.registry.Bus.Profile
        self.message_model = self.registry.Bus.Message
        self.producer_model = self.registry.Bus.Message.Producer
        self.consumer_model = self.registry.Bus.Message.Consumer

    def test_get_profile(self):
        message = self.message_model.insert(
            message=self.test_message, type='producer'
        )
        with self.assertRaises(Exception):
            message.get_profile('Profile 1')
        profile = self.profile_model.insert(
            name='Profile 1', url='fake.url.org',
        )
        res = message.get_profile('Profile 1')
        self.assertEquals(res, profile)

    @mock.patch('pika.BlockingConnection')
    @mock.patch('pika.channel.Channel')
    @mock.patch('pika.BasicProperties')
    def test_publish(self, basic_properties, channel, blocking_connection):
        blocking_connection.return_value.channel.return_value.basic_publish.return_value = True
        producer = self.producer_model.insert(
            message=self.test_message, type='producer',
            exchange='test', routing_key='test',
        )
        producers_before = self.producer_model.query().all()
        with LogCapture() as lc:
            producer.publish()
        lc.check(('anyblok_bus.bloks.bus.message', 'INFO', 'Message published {}'.format(producer)))
        producers_after = self.producer_model.query().all()
        self.assertNotEqual(producers_before, producers_after)
        blocking_connection.return_value.channel.return_value.basic_publish.return_value = False
        producer = self.producer_model.insert(
            message=self.test_message, type='producer',
            exchange='test', routing_key='test',
        )
        producers_before = self.producer_model.query().all()
        with LogCapture() as lc:
            with self.assertRaises(Exception):
                producer.publish()
        producers_after = self.producer_model.query().all()
        self.assertEqual(producers_before, producers_after)
