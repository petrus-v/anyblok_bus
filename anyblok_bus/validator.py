# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.common import add_autodocs
from anyblok.model.plugins import ModelPluginBase
from json import loads


class SchemaException(Exception):
    """Simple exception if error with Schema"""


def bus_validator(schema=None):
    autodoc = "Schema validator %(schema)r" % dict(schema=schema)

    if schema is None:
        raise SchemaException("No existing schema")

    if not hasattr(schema, 'load'):
        raise SchemaException("Schema %r have not load method" % schema)

    def wrapper(method):
        add_autodocs(method, autodoc)
        method.is_a_bus_validator = True
        method.schema = schema
        return classmethod(method)

    return wrapper


class ValidatorPlugin(ModelPluginBase):
    """``anyblok.model.plugin`` to allow the build of the
    ``anyblok_bus.bus_validator``
    """

    def initialisation_tranformation_properties(self, properties,
                                                transformation_properties):
        """ Initialise the transform properties

        :param properties: the properties declared in the model
        :param new_type_properties: param to add in a new base if need
        """
        if 'bus_validators' not in transformation_properties:
            transformation_properties['bus_validators'] = {}

    def transform_base_attribute(self, attr, method, namespace, base,
                                 transformation_properties,
                                 new_type_properties):
        """ transform the attribute for the final Model

        :param attr: attribute name
        :param method: method pointer of the attribute
        :param namespace: the namespace of the model
        :param base: One of the base of the model
        :param transformation_properties: the properties of the model
        :param new_type_properties: param to add in a new base if need
        """
        tp = transformation_properties
        if hasattr(method, 'is_a_bus_validator') and method.is_a_bus_validator:
            tp['bus_validators'][attr] = method.schema

    def insert_in_bases(self, new_base, namespace, properties,
                        transformation_properties):
        """Insert in a base the overload

        :param new_base: the base to be put on front of all bases
        :param namespace: the namespace of the model
        :param properties: the properties declared in the model
        :param transformation_properties: the properties of the model
        """
        for validator in transformation_properties['bus_validators']:

            def wrapper(cls, body=None):
                schema = transformation_properties['bus_validators'][validator]
                res = schema.load(loads(body))
                data, error = res.data, res.errors
                if error:
                    raise SchemaException(
                        'Bad Schema validation with error: %r',
                        error
                    )

                return getattr(super(new_base, cls), validator)(body=data)

            wrapper.__name__ = validator
            setattr(new_base, validator, classmethod(wrapper))
