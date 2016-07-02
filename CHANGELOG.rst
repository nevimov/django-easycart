Changle Log
===========

Notable changes to this project are documented in this file.
The project adheres to `Semantic Versioning`_.


Unreleased_
-----------


0.3.0_ -- 2016-07-02
--------------------

Added
~~~~~
* Handling of exceptions caused by invalid POST data inside views
  (the exceptions are suppressed, the client receives a JSON-response
  containing the error and some additional info about it).
  See updated documentation on views (Reference/easycart.views)

* Additional exception classes for invalid item quantity errors:

  - NegativeItemQuantity
  - NonConvertibleItemQuantity
  - TooLargeItemQuantity
  - ZeroItemQuantity


0.2.0_ -- 2016-06-25
--------------------

Added
~~~~~
* Support for Python 2.7+


0.1.1_ -- 2016-06-14
--------------------

Fixed
~~~~~
* Errors on Python 3.4


.. _Semantic Versioning: http://semver.org/.
.. _0.1.1: https://github.com/nevimov/django-easycart/compare/v0.1.0...v0.1.1
.. _0.2.0: https://github.com/nevimov/django-easycart/compare/v0.1.1...v0.2.0
.. _0.3.0: https://github.com/nevimov/django-easycart/compare/v0.2.0...v0.3.0
.. _unreleased: https://github.com/nevimov/django-easycart/compare/v0.2.0...master
