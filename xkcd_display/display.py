""" shows a xkcd panel image on the dedicated display """

import logging
import time

from logging.handlers import SysLogHandler
from service import find_syslog, Service


class XKCDDisplayService(Service):
    def __init__(self):
        super().__init__(name="xkcdd", pid_dir="/tmp")
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)

    def run(self):
        while not self.got_sigterm():
            self.logger.info("I'm working...")
            time.sleep(5)
