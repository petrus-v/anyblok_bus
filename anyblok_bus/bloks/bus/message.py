# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.

from anyblok import Declarations
from anyblok.column import Integer, String, Selection, LargeBinary, Text
from anyblok.config import Configuration
import logging
import pika

logger = logging.getLogger(__name__)

Bus = Declarations.Model.Bus


@Declarations.register(Bus)
class Message:
    """ Namespace Message """
    MESSAGE_TYPE = None

    id = Integer(primary_key=True)
    content_type = String(default='application/json', nullable=False)
    message = LargeBinary(nullable=False)
    type = Selection(
        selections={
            'consumer': 'Consumer',
            'producer': 'Producer'
        },
        nullable=False
    )
    sequence = Integer(default=100, nullable=False)
    error = Text()

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super(Message, cls).define_mapper_args()
        if cls.__registry_name__ == 'Model.Bus.Message':
            mapper_args.update({'polymorphic_on': cls.type})

        mapper_args.update({'polymorphic_identity': cls.MESSAGE_TYPE})
        return mapper_args


@Declarations.register(Bus.Message)
class Consumer(Bus.Message):

    MESSAGE_TYPE = 'consumer'

    id = Integer(
        primary_key=True,
        foreign_key=Bus.Message.use('id').options(ondelete='cascade'),
    )
    queue = String(nullable=False)
    model = String(nullable=False)
    method = String(nullable=False)


@Declarations.register(Bus.Message)
class Producer(Bus.Message):

    MESSAGE_TYPE = 'producer'

    id = Integer(
        primary_key=True,
        foreign_key=Bus.Message.use('id').options(ondelete='cascade'),
    )
    exchange = String(nullable=False)
    routing_key = String(nullable=False)

    def init_connection(self, profile):
        parameters = pika.URLParameters(profile.url)
        return pika.BlockingConnection(parameters)

    def publish(self):
        """ sending message to the exchange """
        profile_name = Configuration.get('bus_profile')
        try:
            with self.registry.begin_nested():  # savepoint
                profile = self.registry.Bus.Profile.query().filter_by(
                    name=profile_name
                ).one_or_none()
                _connection = self.init_connection(profile)
                channel = _connection.channel()
                channel.confirm_delivery()
                if channel.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.routing_key,
                    body=self.message,
                    properties=pika.BasicProperties(
                        content_type=self.content_type, delivery_mode=1
                    )
                ):
                    logger.info("Message published %r", self)
                    self.delete()
                    # if for obscure raison the message can be deleted
                    # then the message that dont break all
                else:
                    raise Exception("Message cannot be published")
        except Exception as e:
            logger.error("publishing failed with : %r", e)
            self.error = str(e)
        finally:
            if channel and not channel.is_closed and not channel.is_closing:
                channel.close()
            if (
                _connection and
                not _connection.is_closed and
                not _connection.is_closing
            ):
                _connection.close()
