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
import codecs

from .labels import LABELS


VERSION = '0.3'

# U+0009, U+000A, U+000C, U+000D, and U+0020.
ASCII_WHITESPACE = '\t\n\f\r '

ASCII_LOWERCASE_MAP = dict(zip(map(ord, string.ascii_uppercase),
                               map(ord, string.ascii_lowercase)))
UTF8_SIG_DECODER = codecs.getdecoder('utf_8_sig')
UTF16_DECODER = codecs.getdecoder('utf_16')
INCREMENTAL_UTF8_SIG_DECODER = codecs.getincrementaldecoder('utf_8_sig')
INCREMENTAL_UTF16_DECODER = codecs.getincrementaldecoder('utf_16')

# Some names in Encoding are not valid Python aliases. Remap these.
PYTHON_NAMES = {
    'iso-8859-8-i': 'iso-8859-8',
    'x-mac-cyrillic': 'mac-cyrillic',
    'macintosh': 'mac-roman',
    'windows-874': 'cp874'}

CACHE = {}


def lookup(label):
    """
    Look for an encoding by its label.
    This is the spec’s `get an encoding
    <http://encoding.spec.whatwg.org/#concept-encoding-get>`_ algorithm.
    Supported labels are listed there.

    :param label: A string.
    :returns:
        An :class:`Encoding` object, or :obj:`None` for an unknown label.

    """
    # ASCII_WHITESPACE is Unicode, so the result of .strip() is Unicode.
    # We want the Unicode version of .translate().
    label = label.strip(ASCII_WHITESPACE).translate(ASCII_LOWERCASE_MAP)
    name = LABELS.get(label)
    if name is None:
        return None
    encoding = CACHE.get(name)
    if encoding is None:
        if name == 'x-user-defined':
            from .x_user_defined import codec_info
        else:
            python_name = PYTHON_NAMES.get(name, name)
            # Any python_name value that gets to here should be valid.
            codec_info = codecs.lookup(python_name)
        encoding = Encoding(name, codec_info)
        CACHE[name] = encoding
    return encoding


def _get_codec_info(encoding):
    """
    Accept either an encoding object or label.

    :param encoding: An :class:`Encoding` object or a label string.
    :returns: A :class:`codecs.CodecInfo` object.
    :raises: :exc:`~exceptions.LookupError` for an unknown label.

    """
    if not hasattr(encoding, 'codec_info'):
        result = lookup(encoding)
        if result is None:
            raise LookupError('Unknown encoding label: %r' % encoding)
        else:
            encoding = result
    return encoding.codec_info


class Encoding(object):
    def __init__(self, name, codec_info):
        self.name = name
        self.codec_info = codec_info

    def __repr__(self):
        return '<Encoding %s>' % self.name


#: The UTF-8 encoding. Should be used for new content and formats.
UTF8 = lookup('utf-8')


def decode(input, fallback_encoding, errors='replace'):
    """
    Decode a single string.

    :param input: A byte string
    :param fallback_encoding:
        An :class:`Encoding` object or a label string.
        Ignored if :obj:`input` has a BOM.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :return: An Unicode string

    """
    codec_info = _get_codec_info(fallback_encoding)
    if input.startswith((b'\xFF\xFE', b'\xFE\xFF')):
        # UTF-16 BOM. Python’s utf_16 skips it and uses it to pick BE or LE.
        decoder = UTF16_DECODER
    elif input.startswith(b'\xEF\xBB\xBF'):
        # UTF-8 BOM. Python’s utf_8_sig skips it.
        decoder = UTF8_SIG_DECODER
    else:
        decoder = codec_info.decode
    return decoder(input, errors)[0]


def encode(input, encoding=UTF8, errors='strict'):
    """
    Encode a single string.

    :param input: An Unicode string.
    :param encoding: An :class:`Encoding` object or a label string.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :return: A byte string.

    """
    return _get_codec_info(encoding).encode(input, errors)[0]


def iter_decode(input, fallback_encoding, errors='replace'):
    """
    “Pull”-based decoder.

    :param input: An iterable of byte strings.
    :param fallback_encoding:
        An :class:`Encoding` object or a label string.
        Ignored if :obj:`input` has a BOM.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :returns: An iterable of Unicode strings.

    """
    # Fail early if `fallback_encoding` is an invalid label.
    decoder = make_incremental_decoder(fallback_encoding, errors)
    return _iter_function(input, decoder, b'')


def iter_encode(input, encoding=UTF8, errors='strict'):
    """
    “Pull”-based encoder.

    :param input: An iterable of Unicode strings.
    :param encoding: An :class:`Encoding` object or a label string.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :returns: An iterable of byte strings.

    """
    # Fail early if `encoding` is an invalid label.
    encoder = make_incremental_encoder(encoding, errors)
    return _iter_function(input, encoder, '')


def _iter_function(input, function, empty):
    for chunck in input:
        output = function(chunck)
        if output:
            yield output
    output = function(empty, True)
    if output:
        yield output


def make_incremental_decoder(fallback_encoding, errors='replace'):
    """
    “Push”-based decoder.

    :param fallback_encoding:
        An :class:`Encoding` object or a label string.
        Ignored if :obj:`input` has a BOM.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :returns:
        An incremental decoder callable like this:

        .. currentmodule:: None
        .. function:: incremental_decoder(input, final=False)

            :param input: A byte string.
            :param final:
                Indicate that no more input is available.
                Must be :obj:`True` if this is the last call.
            :returns: An Unicode string.

    """
    fallback_decoder = _get_codec_info(fallback_encoding).incrementaldecoder
    # Using a mutable dict to simulate nonlocal on Python 2.x
    state = dict(buffer=b'', decoder=None)
    def incremental_decoder(input, final=False):
        decoder = state['decoder']
        if decoder is None:
            buffer = state['buffer'] + input
            if buffer.startswith((b'\xFF\xFE', b'\xFE\xFF')):
                # UTF-16 BOM.
                # Python’s utf_16 skips it and uses it to pick BE or LE.
                decoder = INCREMENTAL_UTF16_DECODER
            elif buffer.startswith(b'\xEF\xBB\xBF'):
                # UTF-8 BOM. Python’s utf_8_sig skips it.
                decoder = INCREMENTAL_UTF8_SIG_DECODER
            elif final or len(buffer) >= 3:
                # No BOM.
                decoder = fallback_decoder
            else:
                # Not enough data yet.
                state['buffer'] = buffer
                return ''
            decoder = state['decoder'] = decoder(errors).decode
            input = buffer
        return decoder(input, final)
    return incremental_decoder


def make_incremental_encoder(encoding=UTF8, errors='strict'):
    """
    “Push”-based encoder.

    :param encoding: An :class:`Encoding` object or a label string.
    :param errors: Type of error handling. See :func:`codecs.register`.
    :raises: :exc:`~exceptions.LookupError` for an unknown encoding label.
    :returns:
        An incremental encoder callable like this:

        .. currentmodule:: None
        .. function:: incremental_encoder(input, final=False)

            :param input: An Unicode string.
            :param final:
                Indicate that no more input is available.
                Must be :obj:`True` if this is the last call.
            :returns: A byte string.

    """
    return _get_codec_info(encoding).incrementalencoder(errors).encode
