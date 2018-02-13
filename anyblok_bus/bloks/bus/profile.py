# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import String, Selection
from marshmallow import Schema, fields
from anyblok_bus.status import MessageStatus
from anyblok_bus.validator import bus_validator
import logging

logger = logging.getLogger(__name__)


class PingSchema(Schema):

    exchange = fields.String(required=True)
    routing_key = fields.String(required=True)
    properties = fields.Dict(required=True)


@Declarations.register(Declarations.Model.Bus)
class Profile:
    """ Namespace Profile """

    name = String(primary_key=True, unique=True, nullable=False)
    description = String()
    url = String(nullable=False)
    state = Selection(
        selections={
            'connected': 'Connected',
            'disconnected': 'Disconnected'
        },
        default='disconnected', nullable=False
    )

    def __str__(self):
        return "%s %s %s %s" % (self.name, self.description, self.url, self.state)

    def __repr__(self):
        return "%s %s %s %s" % (self.name, self.description, self.url, self.state)

    @classmethod
    def get_consumers(cls):
        # (queue name, model, method name)
        import pdb
        pdb.set_trace()
        return [
            ('blok_%s_ping' % cls.env.cr.dbname, cls.name, 'ping'),
        ]

    @bus_validator(PingSchema())
    def ping(self, body=None):
        logger.info('Received ping with body %s', body)
        return MessageStatus.ACK
