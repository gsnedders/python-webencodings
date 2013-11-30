.. include:: ../README.rst

.. toctree::
   :maxdepth: 2


Byte order marks
----------------

When decoding, for compatibility with deployed content,
a `byte order mark <https://en.wikipedia.org/wiki/Byte_order_mark>`_
(also known as BOM)
is considered more authoritative than anything else.
The corresponding U+FFFE code point is not part of the decoded output.

Encoding nevers prepends a BOM,
but the output can start with a BOM
if the input starts with a U+FFFE code point.
In that case encoding then decoding will not round-trip.


Error handling
--------------

As in the stdlib, error handling for encoding defaults to ``strict``:
raise an exception if there is an error.

For decoding however the default is ``replace``, unlike the stdlib.
Invalid bytes are decoded as ``�`` (U+FFFD, the replacement character).
The reason is that when showing legacy content to the user,
it might be better to succeed decoding only part of it rather than blow up.
This is of course not the case is all situations:
sometimes you want stuff to blow up so you can detect errors early.


API
---

.. module:: webencodings

.. autofunction:: lookup

.. autoclass:: Encoding()

.. autodata:: UTF8

.. autofunction:: decode
.. autofunction:: encode
.. autofunction:: iter_decode
.. autofunction:: iter_encode
.. autoclass:: IncrementalDecoder
    :members:
.. autoclass:: IncrementalEncoder
.. autofunction:: ascii_lower
