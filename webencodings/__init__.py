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


def decode(byte_string, label, errors='replace'):
    """
    Decode a byte string with a fallback encoding given by its label.

    **Note:** in accordance with the Encoding standard,
    the default error handling for decode (but not for encode) is ``replace``,
    ie. insert U+FFFD for invalid bytes.

    """
    # Throw on invalid label, even if there is a BOM.
    encoding = lookup(label)
    if byte_string.startswith((b'\xFF\xFE', b'\xFE\xFF')):
        # Python’s utf_16 picks BE or LE based on the BOM.
        encoding = 'utf_16'
    elif byte_string.startswith(b'\xEF\xBB\xBF'):
        # Python’s utf_8_sig skips the BOM.
        encoding = 'utf_8_sig'
    return byte_string.decode(encoding, errors)


def encode(unicode_string, label, errors='strict'):
    """Encode an Unicode string with an encoding given by its label."""
    return unicode_string.encode(lookup(label), errors)


# These two are here for completeness
# and to give a nicer API than "Use utf_8_sig in, utf_8 out".

def utf8_decode(byte_string, errors='strict'):
    """Decode a byte string as UTF-8, skipping any BOM."""
    # Python’s utf_8_sig skips a b'\xEF\xBB\xBF' BOM if there is one,
    # is like utf_8 otherwise.
    return byte_string.decode('utf_8_sig', errors)


def utf8_encode(unicode_string, errors='strict'):
    """Encode an Unicode string as UTF-8."""
    # Encode without a BOM.
    return unicode_string.encode('utf_8', errors)
