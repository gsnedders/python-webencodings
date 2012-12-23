.. include:: ../README.rst

.. toctree::
   :maxdepth: 2


API
---

.. module:: webencodings

.. note::
    In accordance with the Encoding standard,
    the default error handling for iterdecode (but not for iterencode)
    is ``replace``, ie. insert U+FFFD for invalid bytes.

    Detects BOM.

.. autofunction:: lookup
.. autoclass:: Encoding()
    :members:
