""" shows a xkcd panel image on the dedicated display """

import logging
import random
import signal
import time

from logging.handlers import SysLogHandler
from pathlib import Path

from . import dialog
from . import renderer
from .service import find_syslog, Service


class XKCDDisplayService(Service):
    """ background service to drive and controll the xkcd display"""

    def __init__(self, dialogs_directory=None):
        """ initialize the display """
        super().__init__(name="xkcdd", pid_dir="/tmp")
        self._epd = None  # instance will be set property function method
        self.dialogs_directory = dialogs_directory
        self._pointer_pos = {
            "cueball": 5,
            "megan": 9,
            "center": 7,
        }
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)



    @property
    def epd(self):
        """ importing and setting the epaper display module

        importing the epaper module takes some time since it sets up the
        communication with the epaper hardware. We only need the epaper
        instance in the run method.

        This functionality is provided in a separate function to simplify
        testing
        """
        if self._epd is None:
            try:
                from xkcd_epaper import EPD
            except ImportError:
                from .epd_dummy import EPDummy as EPD
            self._epd = EPD()
        return self._epd

    def run(self):
        """ main (background) function to run the display service

        This function needs to be defined for service.Service.

        :param str dialogs_directory:
            directory that holds the dialog textfiles
        """
        if self.dialogs_directory is None:
            raise ValueError("dialog directory not set")
        self.epd.init()
        dialogs_path = Path(self.dialogs_directory)
        dialog_files = self._get_dialog_files(dialogs_path)
        old_selected = None
        while not self.got_sigterm():
            if self.got_signal(signal.SIGHUP, clear=True):
                dialog_files = self._get_dialog_files(dialogs_path)
            new_selected = random.choice(dialog_files)
            self._show_break_picture(old_selected, new_selected)
            self._display_dialog(new_selected)
            old_selected = new_selected
        self._show_goodbye_picture()

    def _get_dialog_files(self, dialogs_directory):
        """ gets all available dialog text files

        :param str dialogs_directory:
            directory that holds the dialog textfiles
        :returns list: list of dialog text file paths
        """
        self.logger.info("reading dialog files")
        all = (f for f in dialogs_directory.iterdir() if f.is_file())
        visible = (f for f in all if not f.stem.startswith("."))
        texts = (f for f in visible if f.suffix == ".txt")
        return list(texts)

    def _display_dialog(self, dialog_file):
        """ displays a dialog

        A dialog consits of multiple lines with a speaker and the related text.
        Each line will be rendered as one image.

        :param pathlib.Path cache_dir: path of the cache directory
        :param pathlib.Path dialog_file: path of the dialog text file
        """
        xkcd_id = dialog_file.stem
        self.logger.info(f"displaying dialog {xkcd_id}")
        raw_transcript = dialog.parse_dialog(dialog_file.read_text())
        transcript = dialog.adjust_narrators(raw_transcript)
        for i, spoken_text in enumerate(transcript):
            self._display_image(spoken_text, image_nr=i)
            # wait time is guessed for now...
            wait = 5 + spoken_text.text.count(" ") * 0.5
            time.sleep(wait)
            if self.got_sigterm():
                break

    def _display_image(self, spoken_text, image_nr):
        """ displays an image on the xkcd display

        :param pathlib.Path cache_dir: path of the cache directory
        :param str xkcd_id: unique identifier of the dialog
        :param int img_nr: image number
        :param str spoken_text: text to display
        """
        self.logger.info("displaying image")
        pixel_iterator = renderer.render_xkcd_image_as_pixels(spoken_text.text)
        if image_nr == 0:
            self.epd.refresh.slow()
        else:
            self.epd.refresh.quick()
        self._move_and_display(spoken_text.speaker, pixel_iterator)

    def _show_break_picture(self, old_selected, new_selected):
        """ displays a picture in between two dialogs

        :param pathlib.Path old_selected: path to the last shown dialog
        :param pathlib.Path new_selected: path to the upcoming dialog
        """
        self.logger.info("rendering break picture")
        if old_selected:
            text = f"Goodbye {old_selected.stem}, Hello {new_selected.stem}"
        else:
            text = f"Starting with {new_selected.stem}"
        pixel_iterator = renderer.render_xkcd_image_as_pixels(text)
        self.epd.refresh.slow()
        self._move_and_display("center", pixel_iterator)
        time.sleep(5)  # a random guess

    def _show_goodbye_picture(self):
        """ displays a goodbye message

        Since an e-ink display is used in the xkcd-display this shows a
        nice goodbye message or just cleans the screen
        """
        self.logger.info("rendering goodbye picture")
        text = "Be excellent to each other"
        pixel_iterator = renderer.render_xkcd_image_as_pixels(text)
        self.epd.refresh.slow()
        self._move_and_display("center", pixel_iterator)
        self.epd.sleep()

    def _move_and_display(self, where, pixel_iterator):
        """ moves the pointer (servo) to a speaker """
        pos = self._pointer_pos.get(where.lower(), self._pointer_pos["center"])
        self.epd.move(pos)
        self.epd.display(pixel_iterator)
        self.epd.move(0)
