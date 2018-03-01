# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations


@Declarations.register(Declarations.Model)
class Bus:
    """ Namespace Bus """

    @classmethod
    def publish(cls, exchange, routing_key, data, contenttype):
        Message = cls.registry.Bus.Message.Producer
        query = Message.query().order_by(Message.sequence.desc())
        last_message = query.limit(1).one_or_none()
        message = Message.insert(
            exchange=exchange,
            routing_key=routing_key,
            content_type=contenttype,
            message=data
        )

        if last_message:
            message.sequence = last_message.sequence + 1

        for m in Message.query().all():
            try:
                with cls.registry.begin_nested():  # savepoint
                    message = Message.query().with_for_update(
                        nowait=True).get(m.id)
                    message.publish()

            except:
                pass
