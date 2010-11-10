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
from time import sleep

class lawn:
    def __init__(self,win,slow_delay,speedy_delay,colors,miss_permyriad,wait):
        self.slow_delay = slow_delay
        self.speedy_delay = speedy_delay
        self.delay = slow_delay
        self.colors = colors
        self.miss_permyriad = miss_permyriad
        self.wait_at_the_end = wait

        (self.garden_h, self.garden_w) = win.getmaxyx()
        self.mower_size = 4
        # the drawing pad is the screen
        # + room for the mower to go beyond the screen on the left and right
        # + room for one blade of cut grass (behind the mower) on each side
        self.scr = curses.newpad(self.garden_h +1,
                                 self.garden_w + 2*self.mower_size + 2)

        self.grass = ';'
        self.cut_grass = ','

        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

        self.normal_attr = curses.color_pair(1)
        if colors:
            self.grass_attr = curses.color_pair(2)
            self.cut_grass_attr = curses.color_pair(2) | curses.A_DIM
            self.motor_attr = curses.color_pair(3) | curses.A_BOLD
        else:
            self.grass_attr = self.normal_attr
            self.cut_grass_attr = self.normal_attr
            self.motor_attr = self.normal_attr

        # init curses
        curses.curs_set(0) # invisible cursor
        self.scr.nodelay(True) # non-blocking getch()

        # paint unmowed lawn
        self.scr.bkgd(ord(self.grass),self.grass_attr)
        self.scr.refresh(0, self.mower_size + 1,
                         0, 0, self.garden_h -1, self.garden_w -1)

    def right_mower(self,y,x):
        # paints the mower going from left to right
        # (y,x) is the position of the blade of grass directly in front of the
        # mower, that is, directly to its right
        self.scr.addstr(y, x - 4, '`',self.normal_attr)
        self.scr.addstr(y, x - 3, '.',self.normal_attr)
        self.scr.addstr(y, x - 2, '=',self.motor_attr)
        self.scr.addstr(y, x - 1, '.',self.normal_attr)

    def left_mower(self,y,x):
        # paints the mower going from right to left
        # (y,x) is the position of the blade of grass directly in front of the
        # mower, that is, directly to its left
        self.scr.addstr(y, x + 1, '.',self.normal_attr)
        self.scr.addstr(y, x + 2, '=',self.motor_attr)
        self.scr.addstr(y, x + 3, '.',self.normal_attr)
        self.scr.addstr(y, x + 4, '\'',self.normal_attr)

    def mow_grass(self,y,x):
        # paints a blade of mowed grass if the mowing succeeds
        if self.miss_permyriad == 0 or randint(0,10000) > self.miss_permyriad:
            self.scr.addstr(y, x, self.cut_grass,self.cut_grass_attr)
        else:
            self.scr.addstr(y, x, self.grass,self.grass_attr)

    def handle_events(self):
        c = self.scr.getch()
        if c == -1:
            return
        
        if 0 <= c < 256:
            c = chr(c)
            if c == ' ':
                if self.delay == self.slow_delay:
                    self.delay = self.speedy_delay
                else:
                    self.delay = self.slow_delay

    def mow(self):
        for y in range(self.garden_h):
            # x ranges for the entire width of the screen + space to park the
            # mower and one blade of cut grass
            for x in range(self.garden_w + self.mower_size + 1):
                # (y,xx) is the position of the blade of grass directly in front
                # of the mower
                if y%2 == 0:
                    xx = x + self.mower_size + 1
                    self.mow_grass(y,xx - (self.mower_size + 1))
                    self.right_mower(y,xx)
                else:
                    xx = (self.garden_w + 2*self.mower_size + 1) \
                        - x - (self.mower_size + 1)
                    self.left_mower(y,xx)
                    self.mow_grass(y,xx + self.mower_size + 1)
                self.scr.refresh(0, self.mower_size + 1,
                                 0, 0, self.garden_h -1, self.garden_w -1)
                self.handle_events()
                sleep(self.delay)
                self.handle_events()
        if self.wait_at_the_end:
            # wait for a keypress when we're done: we don't want the user to
            # miss on her beautifully mown lawn!
            self.scr.nodelay(False)
            self.scr.getch()
            self.scr.nodelay(True)

def start(win):
    l = lawn(win,slow_delay,speedy_delay,colors,miss_permyriad,wait_at_the_end)
    l.mow()

if __name__ == '__main__':
    curses.wrapper(start) # this performs curses initialisation & catches errors
