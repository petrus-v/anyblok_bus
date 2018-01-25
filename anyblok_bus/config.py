# This file is a part of the AnyBlok / Bus project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.config import Configuration
from .release import version
import os


Configuration.applications.update({
    'bus': {
        'prog': 'Bus app for AnyBlok, version %r' % version,
        'description': 'Bus for AnyBlok',
        'configuration_groups': ['bus', 'config', 'database'],
    },
})


Configuration.add_configuration_groups('createdb', ['bus'])
Configuration.add_configuration_groups('updatedb', ['bus'])
Configuration.add_configuration_groups('nose', ['bus'])
Configuration.add_configuration_groups('interpreter', ['bus'])
Configuration.add_configuration_groups('default', ['bus'])

try:
    # import the configuration to get application
    import anyblok_pyramid.config  # noqa
    Configuration.add_configuration_groups('pyramid', ['bus'])
    Configuration.add_configuration_groups('gunicorn', ['bus'])
except ImportError:
    pass


@Configuration.add('bus', label="Bus - broker options",
                   must_be_loaded_by_unittest=True)
def define_bus_broker(group):
    group.add_argument('--bus-profile',
                       default=os.environ.get('ANYBLOK_BUS_PROFILE'),
                       help="Profile to use")
    group.add_argument('--bus-processes', type=int,
                       default=os.environ.get('ANYBLOK_BUS_PROCESSES', 4),
                       help="Number of process")
