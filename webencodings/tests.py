# coding: utf8
"""

    webencodings.tests
    ~~~~~~~~~~~~~~~~~~

    A basic test suite for Encoding.

    :copyright: Copyright 2012 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from __future__ import unicode_literals
from . import (lookup, LABELS, decode, encode, iterdecode, iterencode,
               utf8_decode, utf8_encode)


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
    for name in set(LABELS.values()):
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


def test_iterdecode():
    assert ''.join(iterdecode([], 'latin1')) == ''
    assert ''.join(iterdecode([b''], 'latin1')) == ''
    assert ''.join(iterdecode([b'\xe9'], 'latin1')) == 'é'
    assert ''.join(iterdecode([b'hello'], 'latin1')) == 'hello'
    assert ''.join(iterdecode([b'he', b'llo'], 'latin1')) == 'hello'
    assert ''.join(iterdecode([b'\xc3\xa9'], 'latin1')) == 'Ã©'
    assert ''.join(iterdecode([b'\xEF\xBB\xBF\xc3\xa9'], 'latin1')) == 'é'
    assert ''.join(iterdecode([
        b'', b'\xEF', b'', b'', b'\xBB\xBF\xc3', b'\xa9'], 'latin1')) == 'é'
    assert ''.join(iterdecode([b'\xEF\xBB\xBF'], 'latin1')) == ''
    assert ''.join(iterdecode([b'\xEF\xBB'], 'latin1')) == 'ï»'
    assert ''.join(iterdecode([b'\xFE\xFF\x00\xe9'], 'latin1')) == 'é'
    assert ''.join(iterdecode([b'\xFF\xFE\xe9\x00'], 'latin1')) == 'é'
    assert ''.join(iterdecode([
        b'', b'\xFF', b'', b'', b'\xFE\xe9', b'\x00'], 'latin1')) == 'é'
    assert ''.join(iterdecode([
        b'', b'h\xe9', b'llo'], 'x-user-defined')) == 'h\uF7E9llo'


def test_iterencode():
    assert b''.join(iterencode([], 'latin1')) == b''
    assert b''.join(iterencode([''], 'latin1')) == b''
    assert b''.join(iterencode(['é'], 'latin1')) == b'\xe9'
    assert b''.join(iterencode(['', 'é', '', ''], 'latin1')) == b'\xe9'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16')) == b'\xe9\x00'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16le')) == b'\xe9\x00'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16be')) == b'\x00\xe9'
    assert b''.join(iterencode([
        '', 'h\uF7E9', '', 'llo'], 'x-user-defined')) == b'h\xe9llo'


def test_utf8_decode():
    # No BOM in the decoded string
    assert utf8_decode(b'\xEF\xBB\xBF\xc3\xa9') == 'é'
    assert utf8_decode(b'\xc3\xa9') == 'é'


def test_utf8_encode():
    # No BOM in the encoded string
    assert utf8_encode('é') == b'\xc3\xa9'


def test_x_user_defined():
    encoded = b'2,\x0c\x0b\x1aO\xd9#\xcb\x0f\xc9\xbbt\xcf\xa8\xca'
    decoded = '2,\x0c\x0b\x1aO\uf7d9#\uf7cb\x0f\uf7c9\uf7bbt\uf7cf\uf7a8\uf7ca'
    assert decode(encoded, 'x-user-defined') == decoded
    assert encode(decoded, 'x-user-defined') == encoded
