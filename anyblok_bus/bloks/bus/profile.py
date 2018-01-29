# This file is a part of the AnyBlok / Bus api project
#
#    Copyright (C) 2018 Julien SZKUDLAPSKI <j.szkudlapski@sensee.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok import Declarations
from anyblok.column import String, Selection

@Declarations.register(Declarations.Model.Bus)
class Profile:
    """ Namespace Profile """

    name = String(primary_key=True, unique=True, nullable=False)
    description = String(nullable=False)
    url = String(nullable=False)
    state = Selection(
        selections={
            'connected': 'Connected',
            'disconnected': 'Disconnected'
        },
        default='disconnected', nullable=False)
    
    def __str__(self):
        return "%s %s %s %s" % (self.name, self.description, self.url, self.state)

    def __repr__(self):
        return "%s %s %s %s" % (self.name, self.description, self.url, self.state)
