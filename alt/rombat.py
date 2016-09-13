#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Alle ROM-Dateien, die für Batterie-Speicherung ausgelegt sind, ausgeben"""

import sys
import os

# Von folgender Adresse heruntergeladen:
# http://snippets.dzone.com/posts/show/915
def getch():
    if sys.platform == 'win32':
        import msvcrt
        return msvcrt.getch()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)

def read_gb (fname):
    f = open (fname, 'rb')
    data = f.read()
    f.close()
    byte = data [0x147]
    if (byte == 0x3 or
            byte == 0x6 or
            byte == 0x9 or
            byte == 0xd or
            byte == 0xf or
            byte == 0x10 or
            byte == 0x13 or
            byte == 0x1b or
            byte == 0x1e):
        return os.path.basename (fname)
    else: return None

def calc_snes_check (data, offset):
    checksum = (data [offset + 0x1e], data [offset + 0x1f])
    checkcom = (data [offset + 0x1c], data [offset + 0x1d])
    checkresult = (checksum [0] | checkcom [0], checksum [1] | checkcom [1])
    if checkresult == (0xff, 0xff): return True
    else: return False

def read_snes (fname):
    f = open (fname, 'rb')
    data = f.read()
    f.close()
    headered = (len (data) % 1024) != 0
    if headered: offset = 0x81c0
    else: offset = 0x7fc0
    if not calc_snes_check (data, offset):
        if headered: offset = 0x101c0
        else: offset = 0xffc0
        if not calc_snes_check (data, offset):
            return ('# Datei konnte nicht gelesen werden: ' +
                os.path.basename (fname))
    carttype = data [offset + 0x16]
    ramsize = data [offset + 0x18]
    if ramsize != 0 or carttype == 0x15 or carttype == 0x1a or carttype == 0x2:
        return os.path.basename (fname)
    else: return None

def decode_smd (data):
    offset = 512
    blksize = 16384
    middle = 8192
    buf = []
    block = data [offset: offset + blksize]
    for i in range (middle):
        buf.append (block [i + middle])
        buf.append (block [i])
    return bytes (buf)

def read_md (fname):
    f = open (fname, 'rb')
    data = f.read()
    f.close()
    if data [1: 11] == b'\x03\x00\x00\x00\x00\x00\x00\xAA\xBB\x06':
        data = decode_smd (data)
    if data [0x1a8: 0x1b0] == b'\x00\xFF\x00\x00\x00\xFF\xFF\xFF':
        if data [0x1b0: 0x1b2] == b'\x52\x41': return os.path.basename (fname)
        elif data [0x1b0: 0x1b2] == b'\x20\x20': return None
    return '# Datei konnte nicht gelesen werden: ' + os.path.basename (fname)

def read_nes (fname):
    f = open (fname, 'rb')
    data = f.read()
    f.close()
    if data [: 3] == b'NES':
        if data [6] & 2 == 2: return os.path.basename (fname)
        else: return None
    else:
        return '# Datei konnte nicht gelesen werden: ' + os.path.basename(fname)

if len (sys.argv) != 2:
    print ('Bitte Verzeichnis angeben\n' +
        'Taste zum Beenden drücken', file = sys.stderr)
    getch()
    sys.exit (1)
elif not os.path.exists (sys.argv [1]):
    print ('Verzeichnis nicht gefunden\n' +
        'Taste zum Beenden drücken', file = sys.stderr)
    getch()
    sys.exit (2)

if os.path.isdir (sys.argv [1]):
    pathlist = []
    tree = os.walk (sys.argv [1])
    for dir in tree:
        for file in dir [2]: pathlist.append (os.path.join (dir [0], file))
    flist = []
    for file in pathlist:
        result = None
        if file.lower().endswith ('.gb') or file.lower().endswith ('.gbc'):
            result = read_gb (file)
        elif (file.lower().endswith ('.smc') or
                file.lower().endswith ('.sfc') or
                file.lower().endswith ('.fig')):
            result = read_snes (file)
        elif file.lower().endswith ('.gen') or file.lower().endswith ('smd'):
            result = read_md (file)
        elif file.lower().endswith ('.nes'): result = read_nes (file)
        if result != None: flist.append (result)
    flist.sort()
    outdir = os.path.join (sys.argv [1], '..')
    f = open (os.path.join (outdir, 'output.txt'), 'w')
    for file in flist: f.write (file + '\n')
    f.close()
else:
    print ('Argument muss ein Verzeichnis sein\n' +
        'Taste zum Beenden drücken', file = sys.stderr)
    getch()
    sys.exit (3)
sys.exit (0)