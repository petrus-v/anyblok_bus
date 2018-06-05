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


class BusConfigurationException(Exception):
    """Simple exception if error with Schema"""


def bus_consumer(queue_name=None, schema=None):
    autodoc = "Consumer: queue %r, schema %r" % (queue_name, schema)

    if schema is None:
        raise SchemaException("No existing schema")

    if queue_name is None:
        raise BusConfigurationException("No queue name")

    if not hasattr(schema, 'load'):
        raise SchemaException("Schema %r have not load method" % schema)

    def wrapper(method):
        add_autodocs(method, autodoc)
        method.is_a_bus_consumer = True
        method.schema = schema
        method.queue_name = queue_name
        return classmethod(method)

    return wrapper


class BusConsumerPlugin(ModelPluginBase):
    """``anyblok.model.plugin`` to allow the build of the
    ``anyblok_bus.bus_consumer``
    """

    def initialisation_tranformation_properties(self, properties,
                                                transformation_properties):
        """ Initialise the transform properties

        :param properties: the properties declared in the model
        :param new_type_properties: param to add in a new base if need
        """
        if 'bus_consumers' not in transformation_properties:
            transformation_properties['bus_consumers'] = {}

        if 'bus_consumers' not in properties:
            properties['bus_consumers'] = []

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
        if hasattr(method, 'is_a_bus_consumer') and method.is_a_bus_consumer:
            tp['bus_consumers'][attr] = (method.queue_name, method.schema)

    def insert_in_bases(self, new_base, namespace, properties,
                        transformation_properties):
        """Insert in a base the overload

        :param new_base: the base to be put on front of all bases
        :param namespace: the namespace of the model
        :param properties: the properties declared in the model
        :param transformation_properties: the properties of the model
        """
        for consumer in transformation_properties['bus_consumers']:

            def wrapper(cls, body=None):
                schema = transformation_properties['bus_consumers'][consumer][
                    1]

                schema.context['registry'] = self.registry
                data = schema.load(loads(body))
                return getattr(super(new_base, cls), consumer)(body=data)

            wrapper.__name__ = consumer
            setattr(new_base, consumer, classmethod(wrapper))
            queue, _ = transformation_properties['bus_consumers'][consumer]
            properties['bus_consumers'].append((queue, consumer))
