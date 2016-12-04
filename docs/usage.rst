=====
Usage
=====

To use Django School Library in a project, add it to your `INSTALLED_APPS`:

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
