#!/usr/bin/env python
# -*- coding: utf-8 -*-

# configuration here for maximum user friendship
slow_delay = 0.5    # time in seconds to mow a ; in slow mode (default mode)
speedy_delay = 0.05 # time in seconds to mow a ; in fast mode
delay = slow_delay
colors = True # true or false, no color themes yet
miss_percentage = .3 # percentage of grass that the mower will not cut properly

import curses
from random import randint
from time import sleep

class lawn:
    def __init__(self,win,slow_delay,speedy_delay,colors,miss_percentage):
        self.slow_delay = slow_delay
        self.speedy_delay = speedy_delay
        self.delay = slow_delay
        self.colors = colors
        self.miss_percentage = miss_percentage

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
        if self.miss_percentage == 0 or randint(0,100) > self.miss_percentage:
            self.scr.addstr(y, x, self.cut_grass,self.cut_grass_attr)
        else:
            self.scr.addstr(y, x, self.grass,self.grass_attr)

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
                self.handle_keypress()
                sleep(self.delay)
                self.handle_keypress()
                
def start(win):
    l = lawn(win,slow_delay,speedy_delay,colors,miss_percentage)
    l.mow()

if __name__ == '__main__':
    curses.wrapper(start) # this performs curses initialisation & catches errors
