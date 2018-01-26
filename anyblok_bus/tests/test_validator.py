# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.tests.testcase import DBTestCase
from anyblok_bus.validator import bus_validator, SchemaException
from marshmallow import Schema, fields
from json import dumps
from anyblok import Declarations


class OneSchema(Schema):
    label = fields.String()
    number = fields.Integer()


class TestValidator(DBTestCase):

    def add_in_registry(self, schema=None):

        @Declarations.register(Declarations.Model)
        class Test:

            @bus_validator(schema=schema)
            def decorated_method(cls, body=None):
                return body

    def add_in_registry_on_mixin(self, schema=None):

        @Declarations.register(Declarations.Mixin)
        class TMixin:

            @bus_validator(schema=schema)
            def decorated_method(cls, body=None):
                return body

        @Declarations.register(Declarations.Model)
        class Test(Declarations.Mixin.TMixin):

            @classmethod
            def decorated_method(cls, body=None):
                res = super(Test, cls).decorated_method(body=body)
                res.update(dict(foo='bar'))
                return res

    def add_in_registry_on_core(self, schema=None):

        @Declarations.register(Declarations.Core)
        class Base:

            @bus_validator(schema=schema)
            def decorated_method(cls, body=None):
                return body

        @Declarations.register(Declarations.Model)
        class Test:

            @classmethod
            def decorated_method(cls, body=None):
                res = super(Test, cls).decorated_method(body=body)
                res.update(dict(foo='bar'))
                return res

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
        with self.assertRaises(SchemaException):
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': 'other'}))

    def test_schema_ok_on_mixin(self):
        registry = self.init_registry(self.add_in_registry_on_mixin,
                                      schema=OneSchema())
        self.assertEqual(
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': '1'})),
            {'label': 'test', 'number': 1, 'foo': 'bar'}
        )

    def test_schema_ok_on_core(self):
        registry = self.init_registry(self.add_in_registry_on_core,
                                      schema=OneSchema())
        self.assertEqual(
            registry.Test.decorated_method(
                body=dumps({'label': 'test', 'number': '1'})),
            {'label': 'test', 'number': 1, 'foo': 'bar'}
        )
