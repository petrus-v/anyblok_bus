# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.common import add_autodocs
from anyblok.model.plugins import ModelPluginBase


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
    pass
