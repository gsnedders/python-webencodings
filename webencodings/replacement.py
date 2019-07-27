# coding: utf-8
"""

    webencodings.replacement
    ~~~~~~~~~~~~~~~~~~~~~~~~

    An implementation of the replacement encoding.
    Folows Python's 'undefined' codec.

    :copyright: Copyright 2019 by Open Close
    :license: BSD, see LICENSE for details.

"""

import codecs

### Codec APIs

class Codec(codecs.Codec):

    def encode(self,input,errors='strict'):
        raise UnicodeError("replacement encoding")

    def decode(self,input,errors='strict'):
        raise UnicodeError("replacement encoding")

class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        raise UnicodeError("replacement encoding")

class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        raise UnicodeError("replacement encoding")

class StreamWriter(Codec,codecs.StreamWriter):
    pass

class StreamReader(Codec,codecs.StreamReader):
    pass

### encodings module API

codec_info = codecs.CodecInfo(
    name='replacement',
    encode=Codec().encode,
    decode=Codec().decode,
    incrementalencoder=IncrementalEncoder,
    incrementaldecoder=IncrementalDecoder,
    streamwriter=StreamWriter,
    streamreader=StreamReader,
    )
