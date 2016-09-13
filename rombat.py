#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Alle ROM-Dateien, die für Batterie-Speicherung ausgelegt sind, ausgeben"""


import sys
import os


# Von folgender Adresse heruntergeladen:
# http://snippets.dzone.com/posts/show/915
def getch():
    """Die gute alte getch() Funktion, bekannt aus "conio.h" in C/C++."""
    if sys.platform == 'win32':
        import msvcrt
        return msvcrt.getch()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)


def error(msg, code):
    """Gibt eine Fehlermeldung aus, wartet auf einen Tastendruck und beendet das
    Programm.
    """
    print(msg + '\nTaste zum Beenden drücken', file = sys.stderr)
    getch()
    sys.exit(code)


def get_data(fname):
    """Öffnet eine Datei und gibt die enthaltenen Daten zurück."""
    f = open(fname, 'rb')
    data = f.read()
    f.close()
    return data


def read_gb(fname):
    """Game Boy ROM-Datei analysieren."""
    data = get_data(fname)
    byte = data[0x147]
    return (
        os.path.basename(fname)
        if byte in (0x3, 0x6, 0x9, 0xd, 0xf, 0x10, 0x13, 0x1b, 0x1e) else
        None
    )


def calc_snes_check(data, offset):
    """Versucht zu überprüfen, ob die Check-Summe korrekt ist. Wird gebraucht,
    um herauszufinden, wie groß der Offset des Datenbereichs eines SNES-ROMs
    ist.
    """
    try:
        checksum = (data[offset + 0x1e], data[offset + 0x1f])
        checkcom = (data[offset + 0x1c], data[offset + 0x1d])  # Complement
        checkresult = (checksum[0] | checkcom[0], checksum[1] | checkcom[1])
        return checkresult == (0xff, 0xff)
    except IndexError:
        return False


def read_snes(fname):
    """SNES ROM-Datei analysieren."""
    data = get_data(fname)
    headered = (len(data) % 1024) != 0
    offset = 0x81c0 if headered else 0x7fc0
    
    if not calc_snes_check(data, offset):
        offset = 0x101c0 if headered else 0xffc0
        if not calc_snes_check(data, offset):
            return (
                '# Datei konnte nicht gelesen werden: ' +
                os.path.basename(fname)
            )

    carttype = data[offset + 0x16]
    ramsize = data[offset + 0x18]
    
    return (
        os.path.basename(fname)
        if ramsize != 0 or carttype in (0x15, 0x1a, 0x2) else
        None
    )


def decode_smd(data):
    """Einige Mega Drive Kopierstationen haben Kartenmischen mit den Bytes
    gespielt. Diese Funktion setzt die Bytes wieder in die richtige Reihenfolge
    zusammen.
    """
    offset = 512
    blksize = 16384
    middle = 8192
    buf = []
    block = data[offset: offset + blksize]
    for i in range(middle):
        buf.append(block[i + middle])
        buf.append(block[i])
    return bytes(buf)


def read_md(fname):
    """Mega Drive ROM-Datei analysieren."""
    data = get_data(fname)
    if data[1: 11] == b'\x03\x00\x00\x00\x00\x00\x00\xAA\xBB\x06':
        data = decode_smd(data)
    if data[0x1a8: 0x1b0] == b'\x00\xFF\x00\x00\x00\xFF\xFF\xFF':
        if data[0x1b0: 0x1b2] == b'\x52\x41':
            return os.path.basename(fname)
        elif data[0x1b0: 0x1b2] == b'\x20\x20':
            return None
    return '# Datei konnte nicht gelesen werden: ' + os.path.basename(fname)


def read_nes(fname):
    """NES ROM-Datei analysieren."""
    data = get_data(fname)
    if data[: 3] == b'NES':
        return os.path.basename(fname) if data[6] & 2 != 0 else None
    else:
        return '# Datei konnte nicht gelesen werden: ' + os.path.basename(fname)


def main(args):
    if len(args) != 2:
        error('Bitte Verzeichnis angeben', 1)
    elif not os.path.exists(args[1]):
        error('Verzeichnis nicht gefunden', 2)
    
    if os.path.isdir(args[1]):
        pathlist = []
        tree = os.walk(args[1])
        for dir in tree:
            for file in dir[2]:
                pathlist.append(os.path.join(dir[0], file))
                
        flist = []
        
        for file in pathlist:
            result = None
            
            if file.lower().endswith('.gb') or file.lower().endswith('.gbc'):
                result = read_gb(file)
            elif (file.lower().endswith('.smc') or
                    file.lower().endswith('.sfc') or
                    file.lower().endswith('.fig')):
                result = read_snes(file)
            elif file.lower().endswith('.gen') or file.lower().endswith('smd'):
                result = read_md(file)
            elif file.lower().endswith('.nes'):
                result = read_nes(file)
                
            if result != None:
                flist.append(result)
                
        flist.sort()
        
        outdir = os.path.join(args[1], '..')
        with open(os.path.join(outdir, 'output.txt'), 'w') as f:
            for file in flist:
                f.write(file + '\n')
    else:
        error('Argument muss ein Verzeichnis sein', 3)
    sys.exit(0)


if __name__ == "__main__":
    main(sys.argv)