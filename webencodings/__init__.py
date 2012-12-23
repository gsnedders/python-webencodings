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


VERSION = '0.1'

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

    :param label: A string.
    :returns:
        An :class:`Encoding` object,
        or :obj:`None` if the label is not valid per the standard.

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
            # None of the names should raise:
            codec_info = codecs.lookup(python_name)
        encoding = Encoding(name, codec_info)
        CACHE[name] = encoding
    return encoding


class Encoding(object):
    def __init__(self, name, codec):
        self.name = name
        self._decoder = codec.decode
        self._encoder = codec.encode
        self._incremental_decoder = codec.incrementaldecoder
        self._incremental_encoder = codec.incrementalencoder

    def decode(self, input, errors='replace'):
        """
        Decode a single string.

        :param input: A byte string
        :param errors: Type of error handling. See :func:`codecs.register`.
        :return: An Unicode string

        """
        if input.startswith((b'\xFF\xFE', b'\xFE\xFF')):
            # Python’s utf_16 picks BE or LE based on the BOM.
            decoder = UTF16_DECODER
        elif input.startswith(b'\xEF\xBB\xBF'):
            # Python’s utf_8_sig skips the BOM.
            decoder = UTF8_SIG_DECODER
        else:
            decoder = self._decoder
        return decoder(input, errors)[0]

    def encode(self, input, errors='strict'):
        """
        Encode a single string.

        :param input: An Unicode string.
        :param errors: Type of error handling. See :func:`codecs.register`.
        :return: A byte string.

        """
        return self._encoder(input, errors)[0]

    def iter_decode(self, input, errors='replace'):
        """
        "Pull-based" decoding.

        :param input: An iterable of byte strings.
        :param errors: Type of error handling. See :func:`codecs.register`.
        :returns: An iterable of Unicode strings.

        """
        decoder = self.make_incremental_decoder(errors)
        for chunck in input:
            output = decoder(chunck)
            if output:
                yield output
        output = decoder(b'', True)
        if output:
            yield output

    def iter_encode(self, input, errors='strict'):
        """
        "Pull-based" encoding.

        :param input: An iterable of Unicode strings.
        :param errors: Type of error handling. See :func:`codecs.register`.
        :returns: An iterable of byte strings.

        """
        encoder = self.make_incremental_encoder(errors)
        for chunck in input:
            output = encoder(chunck)
            if output:
                yield output
        output = encoder('', True)
        if output:
            yield output

    def make_incremental_decoder(self, errors='replace'):
        """
        "Push-based" decoding.

        :param errors: Type of error handling. See :func:`codecs.register`.
        :returns:
            An incremental decoder callable like this:

            .. function:: incremental_decoder(input, final=False)

                :param input: A byte string.
                :param final:
                    Indicate that no more input is available.
                    Must be :obj:`True` if this is the last call.
                :returns: An Unicode string.

        """
        class IncrementalDecoder(object):
            def __init__(self, fallback_decoder):
                self.fallback_decoder = fallback_decoder
                self.decoder = None
                self.buffer = b''

            def __call__(self, input, final=False):
                if not self.decoder:
                    self.buffer += input
                    if self.buffer.startswith((b'\xFF\xFE', b'\xFE\xFF')):
                        # Python’s utf_16 picks BE or LE based on the BOM.
                        decoder = INCREMENTAL_UTF16_DECODER
                    elif self.buffer.startswith(b'\xEF\xBB\xBF'):
                        # Python’s utf_8_sig skips the BOM.
                        decoder = INCREMENTAL_UTF8_SIG_DECODER
                    elif final or len(self.buffer) >= 3:
                        decoder = self.fallback_decoder
                    else:
                        # Not enough data yet.
                        return ''
                    self.decoder = decoder(errors).decode
                    input = self.buffer
                return self.decoder(input, final)

        return IncrementalDecoder(self._incremental_decoder)

    def make_incremental_encoder(self, errors='strict'):
        """
        "Push-based" encoding.

        :param errors: Type of error handling. See :func:`codecs.register`.
        :returns:
            An incremental encoder callable like this:

            .. function:: incremental_encoder(input, final=False)

                :param input: An Unicode string.
                :param final:
                    Indicate that no more input is available.
                    Must be :obj:`True` if this is the last call.
                :returns: A byte string.

        """
        return self._incremental_encoder(errors).encode
