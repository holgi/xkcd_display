""" E-Paper dummy interface """

import logging
from logging.handlers import SysLogHandler

from .service import find_syslog


class RefreshDummy:
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

    def sleep(self):
        """ send the display into sleep """
        self.logger.debug("going to sleep")

    def show_and_move(self, pixel_list, quick_refresh=False, move_to=5):
        """ displays an image and moves the servo """
