# coding: utf8
"""

    webencodings.tests
    ~~~~~~~~~~~~~~~~~~

    A basic test suite for Encoding.

    :copyright: Copyright 2012 by Simon Sapin
    :license: BSD, see LICENSE for details.

"""

from __future__ import unicode_literals
from . import lookup, LABELS


def test_labels():
    assert lookup('utf-8').name == 'utf-8'
    assert lookup('Utf-8').name == 'utf-8'
    assert lookup('UTF-8').name == 'utf-8'
    assert lookup('utf8').name == 'utf-8'
    assert lookup('utf8').name == 'utf-8'
    assert lookup('utf8 ').name == 'utf-8'
    assert lookup(' \r\nutf8\t').name == 'utf-8'
    assert lookup('u8') == None  # Python label.
    assert lookup('utf-8 ') == None  # Non-ASCII white space.

    assert lookup('US-ASCII').name == 'windows-1252'
    assert lookup('iso-8859-1').name == 'windows-1252'
    assert lookup('latin1').name == 'windows-1252'
    assert lookup('LATIN1').name == 'windows-1252'
    assert lookup('latin-1') == None
    assert lookup('LATİN1') == None  # ASCII-only case insensitivity.


def test_names_are_valid_python():
    """Encoding name can be used with Python’s .encode()"""
    for name in set(LABELS.values()):
        encoding = lookup(name)
        assert encoding.decode(b'') == ''
        assert encoding.encode('') == b''
        for repeat in [0, 1, 12]:
            assert list(encoding.iter_decode([b''] * repeat)) == []
            assert list(encoding.iter_encode([''] * repeat)) == []
        decoder = encoding.make_incremental_decoder()
        assert decoder(b'') == ''
        assert decoder(b'', final=True) == ''
        encoder = encoding.make_incremental_encoder()
        assert encoder('') == b''
        assert encoder('', final=True) == b''


def test_decode():
    decode = lambda string, label: lookup(label).decode(string)
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
    encode = lambda string, label: lookup(label).encode(string)
    assert encode('é', 'latin1') == b'\xe9'
    assert encode('é', 'utf8') == b'\xc3\xa9'
    assert encode('é', 'utf8') == b'\xc3\xa9'
    assert encode('é', 'utf-16') == b'\xe9\x00'
    assert encode('é', 'utf-16le') == b'\xe9\x00'
    assert encode('é', 'utf-16be') == b'\x00\xe9'


def test_iter_decode():
    iterdecode = lambda string, label: lookup(label).iter_decode(string)
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


def test_iter_encode():
    iterencode = lambda string, label: lookup(label).iter_encode(string)
    assert b''.join(iterencode([], 'latin1')) == b''
    assert b''.join(iterencode([''], 'latin1')) == b''
    assert b''.join(iterencode(['é'], 'latin1')) == b'\xe9'
    assert b''.join(iterencode(['', 'é', '', ''], 'latin1')) == b'\xe9'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16')) == b'\xe9\x00'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16le')) == b'\xe9\x00'
    assert b''.join(iterencode(['', 'é', '', ''], 'utf-16be')) == b'\x00\xe9'
    assert b''.join(iterencode([
        '', 'h\uF7E9', '', 'llo'], 'x-user-defined')) == b'h\xe9llo'


def test_x_user_defined():
    encoded = b'2,\x0c\x0b\x1aO\xd9#\xcb\x0f\xc9\xbbt\xcf\xa8\xca'
    decoded = '2,\x0c\x0b\x1aO\uf7d9#\uf7cb\x0f\uf7c9\uf7bbt\uf7cf\uf7a8\uf7ca'
    encoded = b'aa'
    decoded = 'aa'
    x_user_defined = lookup('x-user-defined')
    assert x_user_defined.decode(encoded) == decoded
    assert x_user_defined.encode(decoded) == encoded
