import math
from math import sqrt
from math import acos
import curses

velx = 1
vely = 0

posx = 0
posy = 0

newx = posx + velx
newy = posy + vely

stdscr = curses.initscr()

def report_progress():
    """progress: 0-10"""
    stdscr.addstr(0, 0, "Moving file: ")
    stdscr.addstr(1, 0, "Total progress: ")
    stdscr.refresh()

report_progress()