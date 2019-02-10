""" shows a xkcd panel image on the dedicated display """

import logging
import random
import signal
import time
import tempfile

from logging.handlers import SysLogHandler
from pathlib import Path

from . import dialog
from . import renderer
from .service import find_syslog, Service, SERVICE_DEBUG


class XKCDDisplayService(Service):
    """ background service to drive and controll the xkcd display"""

    def __init__(self, dialogs_directory=None):
        """ initialize the display """
        super().__init__(name="xkcdd", pid_dir="/tmp")
        self.epd = None  # instance will be set in run() method
        self.dialogs_directory = dialogs_directory

        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)
        #self.logger.addHandler(logging.FileHandler("debug.log"))
        #self.logger.setLevel(logging.DEBUG)
        #self.logger.setLevel(SERVICE_DEBUG)

    def run(self):
        """ main (background) function to run the display service

        This function needs to be defined for service.Service.

        :param str dialogs_directory:
            directory that holds the dialog textfiles
        """
        if self.dialogs_directory is None:
            raise ValueError("dialog directory not set")
        try:
            from xkcd_epaper import EPD
            from xkcd_epaper.config import DATA_START_TRANSMISSION_1
            self.white = DATA_START_TRANSMISSION_1
        except ImportError:
            from .epd_dummy import EPDummy as EPD
            self.white = None
        self.epd = EPD()
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
            self.epd._send_white_image(self.white)
            self.epd.refresh.quick()
        self.epd.display(pixel_iterator)
        # TODO: show image on ePaper display
        # TODO: move pointer to the speaker

    def _show_break_picture(self, old_selected, new_selected):
        """ displays a picture in between two dialogs

        :param pathlib.Path old_selected: path to the last shown dialog
        :param pathlib.Path new_selected: path to the upcoming dialog
        """
        self.logger.info("rendering break picture")
        if old_selected:
            text = f"Goodbye {old_selected.stem}, Hello {new_selected.stem}"
        else:
            text = f"Starting with {new_selected}"
        pixel_iterator = renderer.render_xkcd_image_as_pixels(text)
        self.epd.refresh.slow()
        self.epd.display(pixel_iterator)
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers

    def _show_goodbye_picture(self):
        """ displays a goodbye message

        Since an e-ink display is used in the xkcd-display this shows a
        nice goodbye message or just cleans the screen
        """
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers
        self.logger.info("rendering goodbye picture")
        text = f"Be excellent to each other"
        pixel_iterator = renderer.render_xkcd_image_as_pixels(text)
        self.epd.refresh.slow()
        self.epd.display(pixel_iterator)
