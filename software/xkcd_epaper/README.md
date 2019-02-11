xkcd_epaper
===========

Library for driving the waveshare [4.2\" epaper display][epd] and a servo
motor. The software is mostly derived from the [waveshare example code][wec],
but adapted for the xkcd display project.

Many thanks to Ben Krasnow, who made an excellent [video tutorial][lut] on why
the refresh rate of the original example code takes so long and "flickers"
while updating the screen and how this can be avoided (with some ghosting
remnants).

Example code:

```python

from xkcd_epaper import EPD

# Create an instance
rpi_interface = EPD()

# Initialize the epaper display. This is done in a separate step to reduce
# instatiation time on the Raspberry Pi
rpi_interface.init()

# show a picture and move the servo
# the pixel list must consist of 400 x 300 items (pixels) with pixel intensities
rpi_interface.show_and_move(pixel_list, quick_refresh=False, servo_pos=5)
```


[epd]: https://www.waveshare.com/product/modules/oleds-lcds/e-paper/4.2inch-e-paper.htm
[wec]: https://www.waveshare.com/wiki/File:4.2inch_e-paper_module_code.7z
[lut]: https://benkrasnow.blogspot.com/2017/10/fast-partial-refresh-on-42-e-paper.html

