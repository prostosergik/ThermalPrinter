#!/usr/bin/env python
# coding: utf-8

from serial import Serial
from struct import pack, unpack
from time import sleep
import os
import math


#===========================================================#
# RASPBERRY PI (tested with Raspbian Jan 2012):
# - Ensure that ttyAMA0 is not used for serial console access:
# edit /boot/cmdline.txt (remove all name-value pairs containing
# ttyAMA0) and comment out last line in /etc/inittab.
# - Fix user permissions with "sudo usermod -a -G dialout pi"
# - Reboot
# - Ensure that the SERIALPORT setting is correct below
#
# BEAGLE BONE:
# Mux settings (Ängström 2012.05, also work on ubuntu 12.04):
# echo 1 > /sys/kernel/debug/omap_mux/spi0_sclk
# echo 1 > /sys/kernel/debug/omap_mux/spi0_d0
#===========================================================#


class ThermalPrinter(object):
    """
        Thermal printing library for PORTI-PC40

        If on BeagleBone or similar device, remember to set the mux settings
        or change the UART you are using. See the beginning of this file for
        default setup.

        Thanks to Lauri Kainulainen for the initial script.
        
        @author: Serge Liskovsky

    """

    # default serial port for the Beagle Bone
    #SERIALPORT = '/dev/ttyO2'
    # this might work better on a Raspberry Pi
    # SERIALPORT = '/dev/ttyAMA0'
    SERIALPORT = '/dev/ttyUSB0'

    BAUDRATE = 9600
    TIMEOUT = 3

    CHARS_PER_LINE = 42

    # pixels with more color value (average for multiple channels) are counted as white
    # tweak this if your images appear too black or too white
    # black_threshold = 48
    # pixels with less alpha than this are counted as white
    # alpha_threshold = 127

    printer = None

    _ESC = b'\x1b'
    _GS = b'\x1d'

    def esc(self):
        self.printer.write(self._ESC)

    def gs(self):
        self.printer.write(self._GS)


    def __init__(self, heatTime=80, heatInterval=2, heatingDots=7, serialport=SERIALPORT):

        if not os.path.exists(serialport):
            raise Exception("ERROR: Serial port not found at: %s" % serialport)

        self.printer = Serial(serialport, self.BAUDRATE, timeout=self.TIMEOUT)

        #reset
        self.reset()

    def reset(self):
        self.esc()
        self.esc()
        self.printer.write(b'\x40') # @ - reset 
        sleep(0.2)
        self.esc()
        self.printer.write(b'\x53') # S - standard mode
        # heat up
        sleep(2)
        self.rf()


    def linefeed(self, number=1):
        for _ in range(number):
            self.print(" ") # it's not buggy
            # self.printer.write(b'\x0A') # it's buggy!
            # sleep(0.2)

        # self.printer.write(b'\x00')
        # self.printer.write(1)

    def reset_formatting(self):
        self.rf()

    def rf(self):
        self.small()
        
        self.d_width(False)
        self.d_height(False)
        self.upside_down(False)
        self.expanded(False)
        self.underline(False)
        self.reverse(False)
        self.justify('left')
        self.alt_font(False)


    def small(self):
        # self.size(0,0)
        self.gs()
        self.printer.write(b'\x21')
        self.printer.write(b'\x00')


    def alt_font(self, on=True):
        self.esc()
        self.printer.write(b'\x21')
        if on:
            self.printer.write(b'\x01')
        else:
            self.printer.write(b'\x00')


    def size(self, width=1, height=1): # w:[1-8], h:[1-8], height not recommended over 4

        if width < 1 or width > 8:
            width = 1

        if height < 1 or height > 8:
            height = 1

        font_size = (width-1 + (height-1 << 4))
        b_font_size = font_size.to_bytes(1, byteorder='little')
    
        self.gs()
        self.printer.write(b'\x21')
        self.printer.write(b_font_size)


    def d_width(self, on=True):     
        self.size(2,1)

    def d_height(self, on=True):     
        self.size(1,2)

    def expanded(self, on=True): # right spacing 8 
        # self.esc()
        self.esc()
        self.printer.write(b'\x20') # space
        if on:
            self.printer.write(b'\x08')
        else:
            self.printer.write(b'\x00')

    def bold(self, on=True):
        self.emphasized(on)

    def strong(self, on=True):
        self.emphasized(on)

    def emphasized(self, on=True):
        self.esc()
        self.printer.write(b'\x45') # E
        if on:
            self.printer.write(b'\x01')
        else:
            self.printer.write(b'\x00')

    def underline(self, on=True):
        self.esc()
        # self.esc()
        self.printer.write(b'\x2d')
        if on:
            self.printer.write(b'\x01') 
        else:
            self.printer.write(b'\x00')

    def upside_down(self, on=True):
        self.esc()
        self.printer.write(b'\x7B') #{
        if on:
            self.printer.write(b'\x01') 
        else:    
            self.printer.write(b'\x00') 

    def reverse(self, on=True):
        self.gs()
        self.printer.write(b'\x42') #B 
        if on:
            self.printer.write(b'\x01') 
        else:    
            self.printer.write(b'\x00') 

    def justify(self, align='left'):
        # self.esc()
        self.esc()
        self.printer.write(b'\x61') #a
        if align=="center" or align.lower() == "c":
            self.printer.write(b'\x01') 
        elif align == "right" or align.lower() == "r":    
            self.printer.write(b'\x02') 
        else:
            self.printer.write(b'\x00') # left


    # TEXT
    def print(self, msg=""):
        self.print_text(msg+"\n")


    def print_text(self, msg, chars_per_line=CHARS_PER_LINE):
        """ Print some text defined by msg. If chars_per_line is defined,
            inserts newlines after the given amount. Use normal '\n' line breaks for
            empty lines. """
        if not chars_per_line:
            self.printer.write(str.encode(msg))
            sleep(0.3)
        else:
            l = list(msg)
            le = len(msg)
            for i in range(chars_per_line + 1, le, chars_per_line + 1):
                l.insert(i, '\n')
            self.printer.write(str.encode("".join(l)))
            sleep(0.3)

    # def print_markup(self, markup):
    #     """ Print text with markup for styling.

    #     Keyword arguments:
    #     markup -- text with a left column of markup as follows:
    #     first character denotes style (n=normal, b=bold, u=underline, i=inverse, f=font B)
    #     second character denotes justification (l=left, c=centre, r=right)
    #     third character must be a space, followed by the text of the line.
    #     """
    #     lines = markup.splitlines(True)
    #     for l in lines:
    #         style = l[0]
    #         justification = l[1].upper()
    #         text = l[3:]

    #         if style == 'b':
    #             self.bold()
    #         elif style == 'u':
    #            self.underline()
    #         elif style == 'i':
    #            self.inverse()
    #         elif style == 'f':
    #             self.font_b()

    #         self.justify(justification)
    #         self.print_text(text)
    #         if justification != 'L':
    #             self.justify()

    #         if style == 'b':
    #             self.bold(False)
    #         elif style == 'u':
    #            self.underline(False)
    #         elif style == 'i':
    #            self.inverse(False)
    #         elif style == 'f':
    #             self.font_b(False)


if __name__ == '__main__':
  
    p = ThermalPrinter()
    p.linefeed()
    p.print("Hello, world!")
    p.linefeed()

