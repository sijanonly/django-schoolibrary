=============================
Django School Library
=============================

.. image:: https://badge.fury.io/py/django_schoolibrary.png
    :target: https://badge.fury.io/py/django_schoolibrary

.. image:: https://travis-ci.org/sijanonly/django_schoolibrary.png?branch=master
    :target: https://travis-ci.org/sijanonly/django_schoolibrary

A library app for schools/colleges to set up their library online

Documentation
-------------

The full documentation is at https://django_schoolibrary.readthedocs.io.

Quickstart
----------

Install Django School Library::

    pip install django_schoolibrary

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'library.apps.LibraryConfig',
        ...
    )

Add Django School Library's URL patterns:

.. code-block:: python

    from library import urls as library_urls


    urlpatterns = [
        ...
        url(r'^', include(library_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
