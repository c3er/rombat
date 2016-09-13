#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

def read_smd (fname):
    f = open (fname, 'rb')
    data = f.read()
    f.close()
    offset = 512
    blksize = 16384
    middle = 8192
    buf = []
    block = data [offset: offset + blksize]
    for i in range (middle):
        buf.append (block [i + middle])
        buf.append (block [i])
    f = open ('output.bin', 'wb')
    f.write (bytes (buf))
    f.close()

if len (sys.argv) != 2:
    print ("Bitte Datei angeben", file = sys.stderr)
    sys.exit (2)
elif not os.path.exists (sys.argv [1]):
    print ("Datei nicht gefunden", file = sys.stderr)
    sys.exit (3)

if os.path.isfile (sys.argv [1]): read_smd (sys.argv [1])
sys.exit (0)
