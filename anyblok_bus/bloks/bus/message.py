# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String, LargeBinary, Text
from anyblok_bus.status import MessageStatus
import logging

logger = logging.getLogger(__name__)


@Declarations.register(Declarations.Model.Bus)
class Message:
    """ Namespace Message """
    id = Integer(primary_key=True)
    content_type = String(default='application/json', nullable=False)
    message = LargeBinary(nullable=False)
    sequence = Integer(default=100, nullable=False)
    error = Text()
    queue = String(nullable=False)
    model = String(nullable=False)
    method = String(nullable=False)

    def consume(self):
        logger.info('consume %r', self)
        error = ""
        try:
            Model = self.registry.get(self.model)
            status = getattr(Model, self.method)(body=self.message)
        except Exception as e:
            status = MessageStatus.ERROR
            error = str(e)

        if status is MessageStatus.ERROR or status is None:
            logger.info('%s Finished %s an error %r', self, error)
            self.error = error
        else:
            self.delete()

    @classmethod
    def consume_all(cls):
        query = cls.query().order(cls.sequence)
        for consumer in query.all():
            with cls.registry.begin_nested():  # savepoint
                consumer.consume()
