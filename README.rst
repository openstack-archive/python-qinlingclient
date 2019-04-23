========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/python-qinlingclient.svg
    :target: https://governance.openstack.org/reference/tags/index.html

.. Change things from this point on

====================
python-qinlingclient
====================

This is an OpenStack Client (OSC) plugin for Qinling, an OpenStack
Function as a Service project.

For more information about Qinling see:
https://docs.openstack.org/qinling/latest/

For more information about the OpenStack Client see:
https://docs.openstack.org/python-openstackclient/latest/

* Free software: Apache license
* Documentation: https://docs.openstack.org/python-qinlingclient/latest/
* Release notes: https://docs.openstack.org/releasenotes/python-qinlingclient/
* Source: https://opendev.org/openstack/python-qinlingclient
* Bugs: https://storyboard.openstack.org/#!/project/926

Getting Started
===============

.. note:: This is an OpenStack Client plugin.  The ``python-openstackclient``
          project should be installed to use this plugin.

Qinling client can be installed from PyPI using pip::

    pip install python-qinlingclient

If you want to make changes to the Qinling client for testing and contribution,
make any changes and then run::

    python setup.py develop

or::

    pip install -e .
