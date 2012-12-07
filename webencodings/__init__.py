# coding: utf8
"""

    webencodings
    ~~~~~~~~~~~~

    This is a Python implementation of the `WHATWG Encoding standard
    <http://encoding.spec.whatwg.org/>`. See README for details.

    :copyright: Copyright 2012 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from __future__ import unicode_literals
import string
from .labels import LABELS


# U+0009, U+000A, U+000C, U+000D, and U+0020.
ASCII_WHITESPACE = '\t\n\f\r '

ASCII_LOWERCASE_MAP = dict(zip(map(ord, string.ascii_uppercase),
                               map(ord, string.ascii_lowercase)))


def lookup(label):
    """Return the name of an encoding from a label or raise a LookupError."""
    # ASCII_WHITESPACE is Unicode, so the result of .strip() is Unicode.
    # We want the Unicode version of .translate().
    return LABELS[label.strip(ASCII_WHITESPACE).translate(ASCII_LOWERCASE_MAP)]
