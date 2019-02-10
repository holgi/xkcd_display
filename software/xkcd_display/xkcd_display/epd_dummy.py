""" E-Paper dummy interface """

import logging
from logging.handlers import SysLogHandler

from .service import find_syslog

class RefreshDummy():
    def __init__(self):
        self.logger = logging.getLogger("EPDRefreshDummy")
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)

    def slow(self):
        self.logger.debug("setting slow refresh rate")

    def quick(self):
        self.logger.debug("setting quick refresh rate")


class EPDummy:
    """ Interface for the Waveshare ePaper 4.2" display """

    def __init__(self):
        """ initialize the display """
        self.logger = logging.getLogger("EPDummy")
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)
        self.refresh = RefreshDummy()

    def init(self):
        self.logger.debug("initializing the display")

    def reset(self):
        """ hardware reset

        setting the reset pin from high to low resets the module
        """
        self.logger.debug("sending hardware reset")

    def clear(self):
        """ clear the display with a white image """
        self.logger.debug("clearing display")

    def display(self, pixels):
        """ display an image

        the pixel values should amount to a length of 400 x 300 items
        """
        self.logger.debug("displaying image")

    def sleep(self):
        """ send the display into sleep """
        self.logger.debug("going to sleep")

    def wait_until_idle(self):
        """ wait for the display """
        pass
