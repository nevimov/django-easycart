Easycart
========

**WARNING: This project is not maintained anymore.**

Easycart is a flexible session-based shopping cart application for Django.
It provides plenty of hooks for overriding and extending the way it works.

By installing this app you get:

* Highly-customizable *BaseCart* and *BaseItem* classes to represent the user
  cart and items in it.

* A handy set of reusable components (views, urls and a context processor) for
  the most common tasks. These components are completely optional.

**Requirements**: Python 2.7+/3.4+ Django 1.8+


Resources
---------
* Docs: http://django-easycart.readthedocs.io/
* Source Code: https://github.com/nevimov/django-easycart
* Issue Tracker: https://github.com/nevimov/django-easycart/issues


Contributing
------------

* Fork the project on GitHub.

* Clone the fork to your local machine::

    $ git clone https://github.com/nevimov/django-easycart

* Setup a virtual environment::

    $ cd django-easycart
    $ virtualenv venv
    $ source venv/bin/activate
    $ pip install -U pip
    $ pip install -r requirements-rtd.txt

* Run tests to ensure everything is set up right::

    $ python runtests.py

  You can use *-h* or *--help* to see options available to the script.

* If your change isn't trivial, you may wish to use tox::

    pip install tox
    tox

* Create a topic branch and commit your changes there.

* Push the branch up to GitHub.

* Create a new pull request.
