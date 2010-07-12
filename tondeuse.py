#!/usr/bin/env python
# -*- coding: utf-8 -*-

# configuration here for maximum user friendship
delay = 0.5    # time in seconds to mow a ;
colors = True # true or false, no color themes yet
miss_percentage = 1 # percentage of grass that the mower will not cut properly

from random import randint
from sys import stdout
from time import sleep

# snippet from the internets
def terminal_size():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack('HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ,
        struct.pack('HHHH', 0, 0, 0, 0)))
    return w, h
# /snippet

def home(): stdout.write('\x1b[H')
def save_cursor(): stdout.write('\x1b[s')
def restore_cursor(): stdout.write('\x1b[u')
def cursor_left(): stdout.write('\x1b[D')
def cursor_down(): stdout.write('\x1b[B')

def right_mower(i=4):
    if not colors:
        mower = '`.=.'[max(0,4-i):garden_w + 4 - i]
    elif i >= 4 and i <= garden_w:
        mower = '\x1b[0m`.\x1b[1;31m=\x1b[0m.'
    elif i == garden_w + 1:
        mower = '\x1b[0m`.\x1b[1;31m='
    elif i == garden_w + 2:
        mower = '\x1b[0m`.'
    elif i == garden_w + 3:
        mower = '\x1b[0m`'
    elif i == garden_w + 4 or i == 0:
        mower = ''
    elif i == 1:
        mower = '\x1b[0m.'
    elif i == 2:
        mower = '\x1b[1;31m=\x1b[0m.'
    elif i == 3:
        mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.'
    stdout.write(mower)

def left_mower(i=4):
    if i >= 4 and i <= garden_w:
        if not colors:
            mower = '.=.’'
        else:
            mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.’'
    elif i == garden_w + 1:
        if not colors:
            mower = '=.’'
        else:
            mower = '\x1b[1;31m=\x1b[0m.’'
    elif i == garden_w + 2:
        if not colors:
            mower = '.’'
        else:
            mower = '\x1b[0m.’'
    elif i == garden_w + 3:
        if not colors:
            mower = '’'
        else:
            mower = '\x1b[0m’'
    elif i == garden_w + 4 or i == 0:
        mower = ''
    elif i == 1:
        if not colors:
            mower = '.'
        else:
            mower = '\x1b[0m.'
    elif i == 2:
        if not colors:
            mower = '.='
        else:
            mower = '\x1b[0m.\x1b[1;31m='
    elif i == 3:
        if not colors:
            mower = '.=.'
        else:
            mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.'
    stdout.write(mower)

mower_size = 4

uncut_grass = ';'
if colors:
    uncut_grass = '\x1b[1;32m' + uncut_grass

grass = ','
if colors:
    grass = '\x1b[0;32m' + grass

def cut_grass():
    if miss_percentage == 0 or randint(0,100) > miss_percentage:
        g = grass
    else:
        g = uncut_grass
    stdout.write(g)


(garden_w, garden_h) = terminal_size()

def init():
    # print entire, untrimmed garden and return to top-left corner and save position
    stdout.write('\x1b[?25l') # no cursor
    stdout.write('\x1b[H\x1b[2J') # wipe out screen
    stdout.write((uncut_grass * garden_w)*garden_h)
    home()
    save_cursor()
    stdout.flush()

def mow_right(i):
    if i > 4:
        cut_grass()
    save_cursor()
    right_mower(i)
    restore_cursor()

def mow_left(i):
    if i > 1:
        cursor_left()
    save_cursor()
    left_mower(i)
    if i > 4:
        cut_grass()
    restore_cursor()


def mow_lawn():
    for j in range(garden_h):
        for i in range(garden_w + mower_size + 1):
            if j%2 == 0:
                mow_right(i)
            else:
                mow_left(i)
            stdout.flush()
            sleep(delay)
        cursor_down()

if __name__ == '__main__':
    try:
        init()
        mow_lawn()
    except:
        stdout.write('\x1b[?25h\x1b[H\x1b[2J')
