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
import signal
import time

class lawn:
    def __init__(self,win,slow_delay,speedy_delay,colors,miss_permyriad,wait):
        self.term = win
        self.slow_delay = slow_delay
        self.speedy_delay = speedy_delay
        self.delay = slow_delay
        self.colors = colors
        self.miss_permyriad = miss_permyriad
        self.wait_at_the_end = wait

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

        (self.garden_h, self.garden_w) = self.term.getmaxyx()
        self.mower_size = 4

        self.init_lawn()
        
        # paint unmowed lawn
        self.scr.bkgd(ord(self.grass),self.grass_attr)
        self.refresh_screen()

        # set some curses parameters
        curses.curs_set(0) # invisible cursor

    def init_lawn(self):
        # create a pad for drawing into and puts it on the terminal

        # the drawing pad is the screen
        # + room for the mower to go beyond the screen on the left and right
        # + room for one blade of cut grass (behind the mower) on each side
        self.scr = curses.newpad(self.garden_h +1,
                                 self.garden_w + 2*self.mower_size + 2)

        self.scr.nodelay(True) # non-blocking getch()

    def right_mower(self,y,x):
        # paint the mower going from left to right
        # (y,x) is the position of the blade of grass directly in front of the
        # mower, that is, directly to its right
        self.scr.addstr(y, x - 4, '`',self.normal_attr)
        self.scr.addstr(y, x - 3, '.',self.normal_attr)
        self.scr.addstr(y, x - 2, '=',self.motor_attr)
        self.scr.addstr(y, x - 1, '.',self.normal_attr)

    def left_mower(self,y,x):
        # paint the mower going from right to left
        # (y,x) is the position of the blade of grass directly in front of the
        # mower, that is, directly to its left
        self.scr.addstr(y, x + 1, '.',self.normal_attr)
        self.scr.addstr(y, x + 2, '=',self.motor_attr)
        self.scr.addstr(y, x + 3, '.',self.normal_attr)
        self.scr.addstr(y, x + 4, '\'',self.normal_attr)

    def mow_grass(self,y,x):
        # paint a blade of mowed grass if the mowing succeeds
        if self.miss_permyriad == 0 or randint(0,10000) > self.miss_permyriad:
            self.scr.addstr(y, x, self.cut_grass,self.cut_grass_attr)
        else:
            self.scr.addstr(y, x, self.grass,self.grass_attr)

    def handle_events(self):
        c = self.scr.getch()
        if c == -1:
            return

        if c == curses.KEY_RESIZE:
            self.earthquake()
        
        if c == ord(' '):
            if self.delay == self.slow_delay:
                self.delay = self.speedy_delay
            else:
                self.delay = self.slow_delay
            self.ticks = 0
            self.t0 = time.time()

    def mow(self):
        # (self.y, self.x) is the position of the blade of grass
        # directly in front of the mower inside the pad
        (self.y, self.x) = (0, self.mower_size + 1)
        finished = False
        self.t0 = time.time()
        self.ticks = 0

        while not finished:
            # mow some grass
            if self.y % 2 == 0:
                self.mow_grass(self.y, self.x - (self.mower_size + 1))
                self.right_mower(self.y,self.x)
            else:
                self.mow_grass(self.y, self.x + self.mower_size + 1)
                self.left_mower(self.y,self.x)

            # tick
            t = time.time()
            while (t - self.t0 < self.delay * self.ticks):
                self.handle_events()
                # sleep for at most .04s at a time so that resize is not too
                # laggy
                # FIXME: this does not seem to help... it looks like curses
                #        is holding back the notification until the screen is
                #        refreshed for some reason... Refreshing here makes
                #        curses crash if the window is resized...
                time.sleep(min(self.delay * self.ticks - (t - self.t0),0.04))
                t = time.time()
            self.handle_events()
            self.refresh_screen()
            self.ticks = self.ticks + 1

            # update the position of the lawnmower
            if self.y % 2 == 0:
                self.x = self.x + 1
            else:
                self.x = self.x - 1
            
            if self.y % 2 == 0 and self.x > self.garden_w + 2*self.mower_size + 1:
                self.y = self.y + 1
                self.x = self.garden_w + self.mower_size
            elif self.y % 2 == 1 and self.x < 0:
                self.y = self.y + 1
                self.x = self.mower_size + 1
            if self.y > self.garden_h:
                finished = True
        
        self.epilogue()

    def epilogue(self):
        # We're done mowing.

        if self.wait_at_the_end:
            # wait for a keypress when we're done: we don't want the user to
            # miss on her beautifully mown lawn!
            self.scr.nodelay(False)
            while (self.scr.getch() != ord(' ')): pass
            self.scr.nodelay(True)

    def earthquake(self):
        # The terminal has been resized! Take action.
        (old_h, old_w) = (self.garden_h, self.garden_w)
        old_x = self.x
        old_scr = self.scr
        
        (self.garden_h, self.garden_w) = self.term.getmaxyx()
        if self.y % 2 == 0:
            self.x = min(old_x, self.garden_w + 2*self.mower_size +1)
        else:
            self.x = min(old_x, self.garden_w + self.mower_size)

        # get a new curses pad to the right dimensions
        self.init_lawn()

        # fill the new pad with the relevant portion of the old one
        self.scr.bkgd(ord(self.grass), self.grass_attr)
        old_scr.overwrite(self.scr)

        # re-mow up to the current position
        # be careful not to re-draw mowed lawn that is already on screen,
        # especially since the new positions of mismowed blades of grass will
        # probably not match those of the old ones.
        for y in range(min(self.y, self.garden_h + 1)):
            for x in range(old_w, self.garden_w + 1):
                self.mow_grass(y, x + self.mower_size)

        if self.y > self.garden_h:
            # if we're passed the bottom of the screen, refresh and call it a day
            self.refresh_screen()
            return

        if self.y % 2 == 1:
            for x in range(old_x, self.garden_w + 1):
                self.mow_grass(self.y, x + self.mower_size)
        
        if self.y % 2 == 0:
            self.right_mower(self.y, self.x)
        else:
            self.left_mower(self.y, self.x)

        self.refresh_screen()
        
    def refresh_screen(self):
        self.scr.refresh(0, self.mower_size + 1,
                         0, 0, self.garden_h -1, self.garden_w -1)

def start(win):
    l = lawn(win,slow_delay,speedy_delay,colors,miss_permyriad,wait_at_the_end)
    l.mow()

if __name__ == '__main__':
    curses.wrapper(start) # this performs curses initialisation & catches errors
