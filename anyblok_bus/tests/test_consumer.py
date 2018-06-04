# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_bus.consumer import (
    bus_consumer, SchemaException, BusConfigurationException)
from marshmallow import Schema, fields
from json import dumps
from anyblok import Declarations
from marshmallow.exceptions import ValidationError


class OneSchema(Schema):
    label = fields.String()
    number = fields.Integer()


class TestValidator(DBTestCase):

    def add_in_registry(self, schema=None):

        @Declarations.register(Declarations.Model)
        class Test:

            @bus_consumer(queue_name='test', schema=schema)
            def decorated_method(cls, body=None):
                return body

    def test_whithout_schema(self):
        with self.assertRaises(SchemaException):
            self.init_registry(self.add_in_registry, schema=None)

    def test_schema_whitout_load_method(self):

        class WrongSchema:
            pass

        with self.assertRaises(SchemaException):
            self.init_registry(self.add_in_registry, schema=WrongSchema)

    def test_schema_ok(self):
        registry = self.init_registry(self.add_in_registry, schema=OneSchema())
        self.assertEqual(
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': '1'})),
            {'label': 'test', 'number': 1}
        )

    def test_schema_ko(self):
        registry = self.init_registry(self.add_in_registry, schema=OneSchema())
        with self.assertRaises(ValidationError):
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': 'other'}))

    def test_decorator_without_name(self):
        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

        with self.assertRaises(BusConfigurationException):
            self.init_registry(add_in_registry)

    def test_decorator_with_twice_the_same_name(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method1(cls, body=None):
                    return body

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method2(cls, body=None):
                    return body

        with self.assertRaises(BusConfigurationException):
            self.init_registry(add_in_registry)

    def test_decorator_with_twice_the_same_name2(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

            @Declarations.register(Declarations.Model)
            class Test2:

                @bus_consumer(queue_name='test', schema=OneSchema())
                def decorated_method(cls, body=None):
                    return body

        with self.assertRaises(BusConfigurationException):
            self.init_registry(add_in_registry)

    def test_with_two_decorator(self):

        def add_in_registry():
            @Declarations.register(Declarations.Model)
            class Test:

                @bus_consumer(queue_name='test1', schema=OneSchema())
                def decorated_method1(cls, body=None):
                    return body

                @bus_consumer(queue_name='test2', schema=OneSchema())
                def decorated_method2(cls, body=None):
                    return body

        registry = self.init_registry_with_bloks(('bus',), add_in_registry)
        self.assertEqual(len(registry.Bus.Profile.get_consumers()), 2)

    def test_consumer_add_in_get_profile(self):
        registry = self.init_registry_with_bloks(
            ('bus',), self.add_in_registry, schema=OneSchema())
        self.assertEqual(registry.Bus.Profile.get_consumers(),
                         [('test', registry.Test, 'decorated_method')])
