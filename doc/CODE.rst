.. This file is a part of the AnyBlok / Bus project
..
..    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
..
.. This Source Code Form is subject to the terms of the Mozilla Public License,
.. v. 2.0. If a copy of the MPL was not distributed with this file,You can
.. obtain one at http://mozilla.org/MPL/2.0/.

.. contents::

Code
====

Declare a consumer on queue with a marshmallow schema
-----------------------------------------------------

.. automodule:: anyblok_bus.consumer


decorator ``bus_consumer``
``````````````````````````
.. autofunction:: bus_consumer
    :noindex:


anyblok model plugin
````````````````````

.. autoclass:: BusConsumerPlugin
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

Worker
------

.. automodule:: anyblok_bus.worker

.. autoclass:: Worker
    :members:
    :undoc-members:
    :show-inheritance:
    :noindex:

Exceptions
``````````

.. autoexception:: SchemaException
    :show-inheritance:
    :noindex:

.. autoexception:: BusConfigurationException
    :show-inheritance:
    :noindex:
