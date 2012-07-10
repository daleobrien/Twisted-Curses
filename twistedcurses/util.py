

import fcntl
import termios
import struct
import curses


def get_real_termial_size():

    try:
        size = struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ, '1234'))
        return size
    except:
        w = curses.tigetnum('cols')
        h = curses.tigetnum('lines')
        return (h, w)

#
