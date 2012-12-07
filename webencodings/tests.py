# coding: utf8
"""

    webencodings.tests
    ~~~~~~~~~~~~~~~~~~

    A basic test suite for Encoding.

    :copyright: Copyright 2012 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from __future__ import unicode_literals
from . import lookup, LABELS, decode, encode, utf8_decode, utf8_encode


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


def test_names_are_valid_python():
    """Encoding name can be used with Python’s .encode()"""
    # TODO: implement x-user-defined
    for name in set(LABELS.values()) - set(['x-user-defined']):
        assert ''.encode(name) == b''


def test_decode():
    assert decode(b'\x80', 'latin1') == '€'
    assert decode(b'\xc3\xa9', 'utf8') == 'é'
    assert decode(b'\xc3\xa9', 'ascii') == 'Ã©'
    assert decode(b'\xEF\xBB\xBF\xc3\xa9', 'ascii') == 'é'  # UTF-8 with BOM

    assert decode(b'\xFE\xFF\x00\xe9', 'ascii') == 'é'  # UTF-16-BE with BOM
    assert decode(b'\xFF\xFE\xe9\x00', 'ascii') == 'é'  # UTF-16-LE with BOM
    assert decode(b'\xFE\xFF\xe9\x00', 'ascii') == '\ue900'
    assert decode(b'\xFF\xFE\x00\xe9', 'ascii') == '\ue900'

    assert decode(b'\x00\xe9', 'UTF-16BE') == 'é'
    assert decode(b'\xe9\x00', 'UTF-16LE') == 'é'
    assert decode(b'\xe9\x00', 'UTF-16') == 'é'

    assert decode(b'\xe9\x00', 'UTF-16BE') == '\ue900'
    assert decode(b'\x00\xe9', 'UTF-16LE') == '\ue900'
    assert decode(b'\x00\xe9', 'UTF-16') == '\ue900'


def test_encode():
    assert encode('é', 'latin1') == b'\xe9'
    assert encode('é', 'utf8') == b'\xc3\xa9'
    assert encode('é', 'utf8') == b'\xc3\xa9'
    assert encode('é', 'utf-16') == b'\xe9\x00'
    assert encode('é', 'utf-16le') == b'\xe9\x00'
    assert encode('é', 'utf-16be') == b'\x00\xe9'


def test_utf8_decode():
    # No BOM in the decoded string
    assert utf8_decode(b'\xEF\xBB\xBF\xc3\xa9') == 'é'
    assert utf8_decode(b'\xc3\xa9') == 'é'


def test_utf8_encode():
    # No BOM in the encoded string
    assert utf8_encode('é') == b'\xc3\xa9'
