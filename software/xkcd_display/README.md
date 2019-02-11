XKCD Display
============


Software to display [xkcd][] dialogs on the dedicated xkcd display.


Modules in this package
-----------------------


### cli

The cli module defines the command line interface. There are four commands you
can use to controll the display:

- `xkcd start DIALOGS_DIRECTORY`: start the xkcd display
- `xkcd status`: check if the xkcd display is running
- `xkcd reload`: gracefully reload.
  refreshes the list of dialogs to display without stopping and starting again
- `xkcd stop`: stop the xkcd display, show a good-bye message

There is one additional command to preview rendered dialogs:
`xkcdtest DIALOGFILE`.

You can use the `--help` option on all commands to get a help message on the
command line.


### dialog

Reads a dialog in a text file and prepares it for later use


### display

This module defines the xkcd display service and implements the start, stop,
reload and status methods used in the command line interface.


### epd_dummy

A dummy implementation of the hardware interface found in the `xkcd_epaper`
package. mainly used for testing.


#### renderer

This module does the heavy lifting. I takes parsed dialogs, figures out the
best parameters and renders the images.

The module uses the [wand][pyw] bindings to [imagemagick][mag], that must be
installed separately. While exploring this I also tried [pillow][pil]. It
worked but I think the rendering engine of wand produced nicer results.


### service

This is a modified version of the [service package][ser] by Florian Brucker,
also known as torfsen. This will be in the requirements, if my pull request
gets accepted.


[xkcd]: http://xkcd.com
[pyw]: http://docs.wand-py.org/
[mag]: https://www.imagemagick.org
[pil]: https://pillow.readthedocs.io
[ser]: https://github.com/torfsen/service
