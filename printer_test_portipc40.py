from lib.portipc40 import ThermalPrinter


p = ThermalPrinter()
# p.linefeed()
# p.print("Hello, world!")
# p.linefeed()

p.small()
p.size(3,2)
# p.d_height()
p.justify('c')
p.print("5678/912")


# p.small()
# p.alt_font()
# p.print("Small")
# p.alt_font(False)
# p.print("Small")

# p.alt_font(True)
# p.d_width()
# p.print("Double Width")

# p.alt_font(False)
# p.d_width()
# p.print("Double Width")

# p.underline()
# p.print("Underline")

# p.d_height()
# p.print("Double Height")

# p.emphasized()
# p.print("Emphasized")

# p.rf()

# p.expanded()
# p.print("Expanded")

# p.upside_down()
# p.print("Upside Down")

# p.rf()

# p.reverse()
# p.print("Reverse")

# p.rf()

# p.justify('center')
# p.print("center")

# p.justify('right')
# p.print("right")

# p.justify('left')
# p.print("left")


# p.rf()
# p.print("************************")
# p.linefeed()

# p.justify('center')
# p.print("**** CORONA  REPORT ****")
# p.d_width()
# p.print("2020.09.02 19:12")
# p.rf()
# p.linefeed()
# p.print("Total/Active in MNE:")
# p.rf()
# p.justify('center')
# p.expanded()
# p.d_width()
# p.d_height()
# p.print("4672/843")
# p.linefeed()
# p.rf()
# p.d_height()
# p.justify()
# # p.print("Active: " + str(active) + " Budva: "+str(budva))
# p.print("Recovered: 1455")
# # p.small()
# p.linefeed()
# # p.print("Src: "+source)
# # p.linefeed(2)


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

