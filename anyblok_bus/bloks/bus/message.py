# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import Integer, String, Selection, LargeBinary

Bus = Declarations.Model.Bus

@Declarations.register(Bus)
class Message:
    """ Namespace Message """
    MESSAGE_TYPE = None

    id = Integer(primary_key=True)
    content_type = String(nullable=False)
    message = LargeBinary(nullable=False)

    type = Selection(
            selections={
                'consumer':'Consumer',
                'producer':'Producer'
            },
            nullable=False)

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

    id = Integer(primary_key=True,
            foreign_key=Bus.Message.use('id').options(ondelete='cascade'))

    queue = String(nullable=False)

@Declarations.register(Bus.Message)
class Producer(Bus.Message):
    MESSAGE_TYPE = 'producer'

    id = Integer(primary_key=True,
            foreign_key=Bus.Message.use('id').options(ondelete='cascade'))

    exchange = String(nullable=False)
    routing_key = String(nullable=False)

