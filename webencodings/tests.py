"""

    webencodings.tests
    ~~~~~~~~~~~~~~~~~~

    A basic test suite for Encoding.

    :copyright: Copyright 2012 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from __future__ import unicode_literals
from . import lookup


def do_lookup(label):
    """Like lookup(), but returns None instead of raising."""
    try:
        return lookup(label)
    except LookupError:
        return None


def test_labels():
    assert do_lookup('utf-8') == 'utf-8'
    assert do_lookup('Utf-8') == 'utf-8'
    assert do_lookup('UTF-8') == 'utf-8'
    assert do_lookup('utf8') == 'utf-8'
    assert do_lookup('utf8') == 'utf-8'
    assert do_lookup('utf8 ') == 'utf-8'
    assert do_lookup(' \r\nutf8\t') == 'utf-8'
    assert do_lookup('u8') == None  # Python label.
    assert do_lookup('utf-8 ') == None  # Non-ASCII white space.

    assert do_lookup('US-ASCII') == 'windows-1252'
    assert do_lookup('iso-8859-1') == 'windows-1252'
    assert do_lookup('latin1') == 'windows-1252'
    assert do_lookup('LATIN1') == 'windows-1252'
    assert do_lookup('latin-1') == None
    assert do_lookup('LATİN1') == None  # ASCII-only case insensitivity.
