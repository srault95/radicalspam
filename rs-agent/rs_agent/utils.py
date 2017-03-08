# -*- coding: utf-8 -*-

import gzip
import base64
import email
import uuid
import hashlib

from six import StringIO

def decompress(filepath):
    with gzip.open(filepath) as fp:
        fileobj = StringIO(fp.read())
        return fileobj

def message_from_filepath(filepath):
    import email
    fileobj = decompress(filepath)
    return email.message_from_file(fileobj)
