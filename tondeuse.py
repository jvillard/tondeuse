#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import sys

def usage():
    print "Usage: ./tondeuse.py [options]"
    print "  -s, --slow=DELAY     slow delay"
    print "  -f, --fast=DELAY    fast delay"
    print "      --nocolor       self explanatory"
    print "      --miss=RATE     miss per myriad"
    print "      --nowait        do not wait at the end"
    
try:
    opts, args = getopt.getopt(sys.argv[1:], "s:f:h", ["slow=", "fast=", "nocolor", "miss=","nowait"])
except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)
        
slow_delay = 0.5 # time in seconds to mow a ; in slow mode (default mode)
speedy_delay = 0.05 # time in seconds to mow a ; in fast mode

colors = True
miss_permyriad = 30
wait_at_the_end = True # shall we wait for a keypress once the lawn is mown?

for o,a in opts:
    if o in ("-s", "--slow"):
        slow_delay = float(a)
    elif o in ("-f", "--fast"):
        speedy_delay = float(a)
    elif o in ("-h"):
        usage()
        sys.exit(0)
    elif o in ("--nocolor"):
        colors = False
    elif o in ("--miss="):
        miss_permyriad = float(a)
    elif o in ("--nowait"):
        wait_at_the_end = False
        

import curses
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


class lawn:
    def __init__(self,slow_delay,speedy_delay,colors,miss_permyriad):
        self.slow_delay = slow_delay
        self.speedy_delay = speedy_delay
        self.delay = slow_delay
        self.colors = colors
        self.miss_permyriad = miss_permyriad

        (self.garden_w, self.garden_h) = terminal_size()
        self.mower_size = 4

        self.uncut_grass = ';'
        if self.colors:
            self.uncut_grass = '\x1b[1;32m' + self.uncut_grass

        self.grass = ','
        if self.colors:
            self.grass = '\x1b[0;32m' + self.grass
        
        # init curses
        self.scr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.scr.nodelay(True)
        stdout.flush()
        
        # print entire, untrimmed garden and return to top-left corner and save position
        stdout.write('\x1b[?25l') # no cursor
        stdout.write('\x1b[H\x1b[2J') # wipe out screen
        stdout.write(self.uncut_grass)
        # replaces stdout.write((self.uncut_grass * self.garden_w)*self.garden_h)
        # which mysteriously doesn't work with curses
        self.scr.bkgd(ord(';'),curses.COLOR_GREEN)
        home()
        save_cursor()
        stdout.flush()


    def deinit(self):
        curses.endwin()
        stdout.write('\x1b[?25h')


    def right_mower(self,i=4):
        if not self.colors:
            mower = '`.=.'[max(0,4-i):self.garden_w + 4 - i]
        elif i >= 4 and i <= self.garden_w:
            mower = '\x1b[0m`.\x1b[1;31m=\x1b[0m.'
        elif i == self.garden_w + 1:
            mower = '\x1b[0m`.\x1b[1;31m='
        elif i == self.garden_w + 2:
            mower = '\x1b[0m`.'
        elif i == self.garden_w + 3:
            mower = '\x1b[0m`'
        elif i == self.garden_w + 4 or i == 0:
            mower = ''
        elif i == 1:
            mower = '\x1b[0m.'
        elif i == 2:
            mower = '\x1b[1;31m=\x1b[0m.'
        elif i == 3:
            mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.'
        stdout.write(mower)

    def left_mower(self,i=4):
        if i >= 4 and i <= self.garden_w:
            if not self.colors:
                mower = '.=.\''
            else:
                mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.\''
        elif i == self.garden_w + 1:
            if not self.colors:
                mower = '=.\''
            else:
                mower = '\x1b[1;31m=\x1b[0m.\''
        elif i == self.garden_w + 2:
            if not self.colors:
                mower = '.\''
            else:
                mower = '\x1b[0m.\''
        elif i == self.garden_w + 3:
            if not self.colors:
                mower = '\''
            else:
                mower = '\x1b[0m\''
        elif i == self.garden_w + 4 or i == 0:
            mower = ''
        elif i == 1:
            if not self.colors:
                mower = '.'
            else:
                mower = '\x1b[0m.'
        elif i == 2:
            if not self.colors:
                mower = '.='
            else:
                mower = '\x1b[0m.\x1b[1;31m='
        elif i == 3:
            if not self.colors:
                mower = '.=.'
            else:
                mower = '\x1b[0m.\x1b[1;31m=\x1b[0m.'
        stdout.write(mower)


    def cut_grass(self):
        if self.miss_permyriad == 0 or randint(0,10000) > self.miss_permyriad:
            g = self.grass
        else:
            g = self.uncut_grass
        stdout.write(g)


    def mow_right(self,i):
        if i > 4:
            self.cut_grass()
        save_cursor()
        self.right_mower(i)
        restore_cursor()

    def mow_left(self,i):
        if i > 1:
            cursor_left()
        save_cursor()
        self.left_mower(i)
        if i > 4:
            self.cut_grass()
        restore_cursor()

    def handle_keypress(self):
        c = self.scr.getch()
        if c == -1:
            return
        c = chr(c)
        if c == ' ':
            if self.delay == self.slow_delay:
                self.delay = self.speedy_delay
            else:
                self.delay = self.slow_delay

    def mow(self):
        for j in range(self.garden_h):
            for i in range(self.garden_w + self.mower_size + 1):
                if j%2 == 0:
                    self.mow_right(i)
                else:
                    self.mow_left(i)
                stdout.flush()
                self.handle_keypress()
                sleep(self.delay)
                self.handle_keypress()
            cursor_down()

        if wait_at_the_end:
            # wait for a keypress when we're done: we don't want the user to miss
            # on his beautifully mown lawn!
            self.scr.nodelay(False)
            self.scr.getch()
            self.scr.nodelay(True)


if __name__ == '__main__':
    try:
        l = 0
        l = lawn(slow_delay,speedy_delay,colors,miss_permyriad)
        l.mow()
        l.deinit()
    except:
        if l:
            l.deinit()
        else:
            curses.endwin()
            stdout.write('\x1b[?25h')
