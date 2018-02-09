# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from anyblok_bus.bloks.bus.message import Message
from logging import getLogger
from pika import SelectConnection, URLParameters

logger = getLogger(__name__)


class Worker:

    def __init__(self, registry, profile):
        self.registry = registry
        self.profile = profile
        self._connection = None
        self._channel = None
        self._closing = False

    def connect(self):
        """ Creating connection object """
        url = self.get_url()
        logger.info('Connecting to %s', url)
        return SelectConnection(
            URLParameters(url),
            self.on_connection_open,
            stop_ioloop_on_close=False
        )

    def reconnect(self):
        self._connection.ioloop.stop()
        if not self._closing:
            # TODO: use start() method ?
            self._connection = self.connect()
            self._connection.ioloop.start()

    def get_url(self):
        """ Retrieve connection url """
        connection = self.profile
        if connection:
            return connection.url
        raise Exception("Unknown profile")

    def on_connection_open(self, *a):
        """ Called when we are fully connected to RabbitMQ """
        self._connection.add_on_close_callback(self.on_connection_closed)
        self._connection.channel(on_open_callback=self.on_channel_open)
        logger.info('Connexion opened')

    def on_channel_open(self, channel):
        """ Called when channel is opened """
        logger.info('Channel opened')
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        # TODO: adapter cette partie au fonctionnement souhaitée
        # d'après la doc pika : on déclare un exchange, puis lorsque l'exchange est ok,
        # on déclare une queue, lorsque la queue est ok on met en place lien entre la queue et l'exchange,
        # enfin on démarre la "consommation" de la queue
        for queue, model, method in self.registry.Consumer.query().all():
            self.declare_consumer(queue, model, method)

    def on_channel_closed(self, channel, reply_code, reply_text):
        """ Called when channel is closed """
        logger.warning(
            'Channel %i was closed: (%s) %s', channel, reply_code, reply_text
        )
        self._connection.close()

    def on_connection_closed(self, connection, reply_code, reply_text):
        """ Called when connection is closed """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            logger.warning(
                'Connection closed, reopening in 5 seconds: (%s) %s',
                reply_code, reply_text
            )
            self._connection.add_timeout(5, self.reconnect)

    def declare_consumer(self, queue, model, method):


    def start(self):
        """ Creating connection object and starting event loop """
        logger.info('start')
        self._connection = self.connect()
        self._connection.ioloop.start()

    def stop(self):
        logger.info('stop')
