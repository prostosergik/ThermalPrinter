#!/usr/bin/env python
# coding: utf-8

from serial import Serial
from struct import pack, unpack
from time import sleep
import os


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
        Thermal printing library for Custom DPT100-S printer (www.custom.it) 

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

    BAUDRATE = 19200
    TIMEOUT = 3

    # pixels with more color value (average for multiple channels) are counted as white
    # tweak this if your images appear too black or too white
    black_threshold = 48
    # pixels with less alpha than this are counted as white
    alpha_threshold = 127

    printer = None

    _ESC = b'\x1b'
    _GS = b'\x1d'

    def __init__(self, heatTime=80, heatInterval=2, heatingDots=7, serialport=SERIALPORT):

        if not os.path.exists(serialport):
            raise Exception("ERROR: Serial port not found at: %s" % serialport)

        self.printer = Serial(serialport, self.BAUDRATE, timeout=self.TIMEOUT)

        #reset
        self.reset()

    # def has_paper(self):
    #     # Check the status of the paper using the printer's self reporting
    #     # ability. SerialTX _must_ be connected!
    #     status = -1
    #     self.printer.write(self._ESC)
    #     self.printer.write(chr(118))
    #     self.printer.write(chr(0))
    #     for i in range(0, 9):
    #         if self.printer.inWaiting():
    #             status = unpack('b', self.printer.read())[0]
    #             break
    #         sleep(0.01)
    #     return not bool(status & 0b00000100)

    def reset(self):
        self.printer.write(self._ESC)
        self.printer.write(b'\x40') # @
        # heat up
        sleep(2)
    
    # be careful!
    def factory_reset(self):
        self.printer.write(self._GS)
        self.printer.write(b'\x55') #U
        self.reset()

    def linefeed(self, number=1):
        for _ in range(number):
            self.printer.write(b'\x0a') #\n

    def small(self):
        self.printer.write(b'\x00')

    def d_width(self):
        self.printer.write(b'\x01')

    def d_height(self):
        self.printer.write(b'\x02')

    def expanded(self):
        self.printer.write(b'\x03')
 
    def restore_small(self):
        self.printer.write(b'\x04')

    def underline(self, on=True):
        self.printer.write(self._ESC)
        if on:
            self.printer.write(b'\x51') #Q
        else:
            self.printer.write(b'\x71') #q

    def reverse(self, on=True):
        self.printer.write(self._ESC)
        if on:
            self.printer.write(b'\x52') #R
        else:    
            self.printer.write(b'\x4e') #N

    #buffer
    def print_buffer(self):
        self.printer.write(b'\x0D')
   
    def cancel_buffer(self):
        self.printer.write(b'\x07')

    #DRAW
    def graphic_mode(self):
        self.printer.write(b'\x11')

    def print_logo(self):         
        self.printer.write(self._ESC)
        self.printer.write(b'\xfa')
        self.printer.write(b'\x01')
        self.printer.write(b'\x55')

    def draw_line(self):
        self.printer.write(self._ESC)
        self.printer.write(b'\x57')
        # next, 48 bytes should be sent.

    # def justify(self, align="L"):
    #     pos = 0
    #     if align == "L":
    #         pos = 0
    #     elif align == "C":
    #         pos = 1
    #     elif align == "R":
    #         pos = 2
    #   lf._ESC)#     self.printer.write(chr(97))
    #     self.printer.write(chr(pos))

#     def barcode_chr(self, msg):
#         self.printer.write(chr(29)) # Leave
#         self.printer.write(chr(72)) # Leave
#         self.printer.write(msg)     # Print barcode # 1:Abovebarcode 2:Below 3:Both 0:Not printed

#     def barcode_height(self, msg):
#         self.printer.write(chr(29))  # Leave
#         self.printer.write(chr(104)) # Leave
#         self.printer.write(msg)      # Value 1-255 Default 50

#     def barcode_height(self):
#         self.printer.write(chr(29))  # Leave
#         self.printer.write(chr(119)) # Leave
#         self.printer.write(chr(2))   # Value 2,3 Default 2

#     def barcode(self, msg):
#         """ Please read http://www.adafruit.com/datasheets/A2-user%20manual.pdf
#             for information on how to use barcodes. """
#       
#         self.printer.write(chr(29))  # LEAVE
#         self.printer.write(chr(107)) # LEAVE
#         self.printer.write(chr(65))  # USE ABOVE CHART
#         self.printer.write(chr(12))  # USE CHART NUMBER OF CHAR
#         self.printer.write(msg)

# I Interleved 2/5
# C Code 39
# B CodaBar
# e EAN8
# E EAN13

# //  Serial.write(0x1B);
# //  Serial.write(0x63);
# //  Serial.write('I'); //type
# //  Serial.write(100); //height
# //  Serial.write(0); //left margin
# //  Serial.write(0b00100111); //options?
# //  Serial.write(12); //length - 1 for some reason
# //  Serial.print("+38268874693"); //data


    # TEXT
    def print(self, msg=""):
        self.print_text(msg+"\n")

    def print_text(self, msg, chars_per_line=None):
        """ Print some text defined by msg. If chars_per_line is defined,
            inserts newlines after the given amount. Use normal '\n' line breaks for
            empty lines. """
        if not chars_per_line:
            self.printer.write(str.encode(msg))
            sleep(0.2)
        else:
            l = list(msg)
            le = len(msg)
            for i in range(chars_per_line + 1, le, chars_per_line + 1):
                l.insert(i, '\n')
            self.printer.write(str.encode("".join(l)))
            sleep(0.2)

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

    def convert_pixel_array_to_binary(self, pixels, w, h):
        """ Convert the pixel array into a black and white plain list of 1's and 0's
            width is enforced to 384 and padded with white if needed. """
        black_and_white_pixels = [1] * 384 * h
        if w > 384:
            print("Bitmap width too large: %s. Needs to be under 384" % w)
            return False
        elif w < 384:
            print("Bitmap under 384 (%s), padding the rest with white" % w)

        print("Bitmap size", w)

        if type(pixels[0]) == int: # single channel
            print(" => single channel")
            for i, p in enumerate(pixels):
                if p < self.black_threshold:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 0
                else:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 1
        elif type(pixels[0]) in (list, tuple) and len(pixels[0]) == 3: # RGB
            print(" => RGB channel")
            for i, p in enumerate(pixels):
                if sum(p[0:2]) / 3.0 < self.black_threshold:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 0
                else:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 1
        elif type(pixels[0]) in (list, tuple) and len(pixels[0]) == 4: # RGBA
            print(" => RGBA channel")
            for i, p in enumerate(pixels):
                if sum(p[0:2]) / 3.0 < self.black_threshold and p[3] > self.alpha_threshold:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 0
                else:
                    black_and_white_pixels[i % w + int(i / w) * 384] = 1
        else:
            print("Unsupported pixels array type. Please send plain list (single channel, RGB or RGBA)")
            print("Type pixels[0]", type(pixels[0]), "haz", pixels[0])
            return False

        return black_and_white_pixels


    def print_bitmap(self, pixels, w, h, output_png=False):
        """ Best to use images that have a pixel width of 384 as this corresponds
            to the printer row width.

            pixels = a pixel array. RGBA, RGB, or one channel plain list of values (ranging from 0-255).
            w = width of image
            h = height of image
            if "output_png" is set, prints an "print_bitmap_output.png" in the same folder using the same
            thresholds as the actual printing commands. Useful for seeing if there are problems with the
            original image (this requires PIL).

            Example code with PIL:
                import Image, ImageDraw
                i = Image.open("lammas_grayscale-bw.png")
                data = list(i.getdata())
                w, h = i.size
                p.print_bitmap(data, w, h)
        """
        counter = 0
        if output_png:
            from PIL import Image, ImageDraw
            test_img = Image.new('RGB', (384, h))
            draw = ImageDraw.Draw(test_img)

        # self.linefeed()

        black_and_white_pixels = self.convert_pixel_array_to_binary(pixels, w, h)
        print_bytes = []

        # read the bytes into an array
        for rowStart in range(0, h, 256):
            chunkHeight = 255 if (h - rowStart) > 255 else h - rowStart
            print_bytes += (18, 42, chunkHeight, 48)

            for i in range(0, 48 * chunkHeight):
                # read one byte in
                byt = 0
                for xx in range(8):
                    pixel_value = black_and_white_pixels[counter]
                    counter += 1
                    # check if this is black
                    if pixel_value == 0:
                        byt += 1 << (7 - xx)
                        if output_png: draw.point((counter % 384, round(counter / 384)), fill=(0, 0, 0))
                    # it's white
                    else:
                        if output_png: draw.point((counter % 384, round(counter / 384)), fill=(255, 255, 255))

                print_bytes.append(byt)
       
        i = 0
        for b in print_bytes:
            if i%48 == 0 and i < len(print_bytes)-48:
                self.draw_line()
            self.printer.write(pack("B", b))
            i = i+1

        if output_png:
            test_print = open('print-output.png', 'wb')
            test_img.save(test_print, 'PNG')
            print("output saved to %s" % test_print.name)
            test_print.close()



# if __name__ == '__main__':
  
#     p = ThermalPrinter(serialport=serialport)
#     p.linefeed()
#     p.print("************************")
#     p.d_width()
#     p.print("06.04.2020. 17:52")
#     p.small()
#     p.linefeed()
#     p.print("Total")
#     p.expanded()
#     p.print("     223    ")
#     p.linefeed()
#     p.d_height()
#     p.print("Tested: 1915   Budva: 4")
#     p.small()
#     p.print("************************")
#     p.linefeed(4)


# #     markup = """bl bold left
# # ur underline right
# # fc font b centred (next line blank)
# # nl
# # il inverse left
# # """
# #     p.print_markup(markup)

#     # runtime dependency on Python Imaging Library
#     from PIL import Image
#     i = Image.open("corona.png")
#     data = list(i.getdata())
#     w, h = i.size
#     p.print_bitmap(data, w, h, True)

