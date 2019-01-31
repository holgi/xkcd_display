""" shows a xkcd panel image on the dedicated display """

import logging
import random
import signal
import time
import tempfile

from logging.handlers import SysLogHandler
from pathlib import Path
from service import find_syslog, Service

from . import dialog
from . import renderer


class XKCDDisplayService(Service):
    """ background service to drive and controll the xkcd display"""

    def __init__(self, dialogs_directory):
        """ initialize the display

        :param str dialogs_directory:
            directory that holds the dialog textfiles
        """
        super().__init__(name="xkcdd", pid_dir="/tmp")
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)
        self.dialogs_directory = Path(dialogs_directory)

    def run(self):
        """ main (background) function to run the display service

        This function needs to be defined for service.Service
        """
        with tempfile.TemporaryDirectory() as cache_dir:
            chache_path = Path(cache_dir)
            dialog_files = self._get_dialog_files()
            while not self.got_sigterm():
                if self.got_signal(signal.SIGHUP, clear=True):
                    dialog_files = self._get_dialog_files()
                    self._clear_cache(chache_path)
                selected = random.choice(dialog_files)
                self._display_dialog(chache_path, selected)
                self._show_break_picture(selected)
            self._show_goodbye_picture()

    def _get_dialog_files(self):
        """ gets all available dialog text files

        :returns list: list of dialog text file paths
        """
        self.logger.info("reading dialog files")
        all = (f for f in self.dialogs_directory.iterdir() if f.is_file())
        visible = (f for f in all if not f.stem.startswith("."))
        texts = (f for f in visible if f.suffix == ".txt")
        return list(texts)

    def _clear_cache(self, cache_dir):
        """ clears the cache directory

        :param pathlib.Path cache_dir: path of the cache directory
        """
        self.logger.info("clearing cache directory")
        for item in cache_dir.iterdir():
            item.unlink()

    def _display_dialog(self, cache_dir, dialog_file):
        """ displays a dialog

        A dialog consits of multiple lines with a speaker and the related text.
        Each line will be rendered as one image.

        :param pathlib.Path cache_dir: path of the cache directory
        :param pathlib.Path dialog_file: path of the dialog text file
        """
        xkcd_id = dialog_file.stem
        self.logger.info("displaying dialog {xkcd_id}")
        raw_transcript = dialog.parse_dialog(dialog_file.read_text())
        transcript = dialog.adjust_narrators(raw_transcript)
        for img_nr, spoken_text in enumerate(transcript):
            self._display_image(cache_dir, xkcd_id, img_nr, spoken_text)
            # wait time is guessed for now...
            wait = 5 + spoken_text.text.count(" ") * 0.5
            time.sleep(wait)

    def _display_image(self, cache_dir, xkcd_id, img_nr, spoken_text):
        """ displays an image on the xkcd display

        :param pathlib.Path cache_dir: path of the cache directory
        :param str xkcd_id: unique identifier of the dialog
        :param int img_nr: image number
        :param str spoken_text: text to display
        """
        self.logger.info("displaying image {xkcd_id} {img_nr}")
        img = self._render(cache_dir, xkcd_id, img_nr, spoken_text)
        # TODO: show image on ePaper display
        # TODO: move pointer to the speaker

    def _render(self, cache_dir, xkcd_id, img_nr, spoken_text):
        """ returns text rendered as an image

        If the image was already cached, it uses the cached version

        :param pathlib.Path cache_dir: path of the cache directory
        :param str xkcd_id: unique identifier of the dialog
        :param int img_nr: image number
        :param str spoken_text: text to display
        :returns bytes: rendered image
        """
        cache_file = cache_dir / f"{xkcd_id}-{img_nr}.png"
        if cache_file.exists():
            self.logger.info("using cached image {xkcd_id} {img_nr}")
            return cache_file.read_bytes()
        else:
            self.logger.info("rendering image {xkcd_id} {img_nr}")
            blob = renderer.render_xkcd_image(spoken_text.text)
            cache_file.write_bytes(blob)
            return blob

    def _show_break_picture(self, selected):
        """ displays a picture in between two dialogs

        :param pathlib.Path selected: path to the last shown dialog
        """
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers
        pass

    def _show_goodbye_picture(self):
        """ displays a goodbye message

        Since an e-ink display is used in the xkcd-display this shows a
        nice goodbye message or just cleans the screen
        """
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers
        pass
