=============
API Reference
=============

.. module:: cosm

The cosm-python library consists of two layers. The top layer uses the
:class:`CosmAPIClient` and object wrappers.  The lower layer via
:class:`Client` gives access directly to sending native python types and
accessing the response.

API Client
==========

.. autoclass:: cosm.CosmAPIClient
    :members:
    :undoc-members:

Feeds, Datastreams and Datapoints
---------------------------------

.. autoclass:: cosm.managers.FeedsManager
    :members:
    :undoc-members:
    :exclude-members: resource

.. autoclass:: cosm.Feed
    :members:
    :undoc-members:
    :exclude-members: id, feed

.. autoclass:: cosm.managers.DatastreamsManager
    :members:
    :undoc-members:
    :exclude-members: resource

.. autoclass:: cosm.Datastream
    :members:
    :undoc-members:

.. autoclass:: cosm.managers.DatapointsManager
    :members:
    :undoc-members:
    :exclude-members: resource

.. autoclass:: cosm.Datapoint
    :members:
    :undoc-members:

Location and Waypoints
----------------------

.. autoclass:: cosm.Location
    :members:
    :undoc-members:

.. autoclass:: cosm.Waypoint
    :members:
    :undoc-members:

API Keys
--------

.. autoclass:: cosm.managers.KeysManager
    :members:
    :undoc-members:

.. autoclass:: cosm.Key
    :members:
    :undoc-members:

.. autoclass:: cosm.Permission
    :members:
    :undoc-members:

.. autoclass:: cosm.Resource
    :members:
    :undoc-members:

Triggers
--------

.. autoclass:: cosm.managers.TriggersManager
    :members:
    :undoc-members:
    :exclude-members: resource

.. autoclass:: cosm.Trigger
    :members:
    :undoc-members:

Low Level Client
================

.. autoclass:: cosm.Client
    :members:
    :undoc-members:
    :show-inheritance:
    :exclude-members: BASE_URL
