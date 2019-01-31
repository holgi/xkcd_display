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
    def __init__(self, dialogs_directory):
        super().__init__(name="xkcdd", pid_dir="/tmp")
        self.logger.addHandler(
            SysLogHandler(
                address=find_syslog(), facility=SysLogHandler.LOG_DAEMON
            )
        )
        self.logger.setLevel(logging.INFO)
        self.dialogs_directory = Path(dialogs_directory)

    def run(self):
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
        self.logger.info("reading dialog files")
        all = (f for f in self.dialogs_directory.iterdir() if f.is_file())
        visible = (f for f in all if not f.stem.startswith("."))
        texts = (f for f in visible if f.suffix == ".txt")
        return list(texts)

    def _clear_cache(self, cache_dir):
        self.logger.info("clearing cache directory")
        for item in cache_dir.iterdir():
            item.unlink()

    def _display_dialog(self, cache_dir, dialog_file):
        xkcd_number = dialog_file.stem
        raw_transcript = dialog.parse_dialog(dialog_file.read_text())
        transcript = dialog.adjust_narrators(raw_transcript)

        for img_nr, spoken_text in enumerate(transcript):
            self._display_image(cache_dir, xkcd_number, img_nr, spoken_text)
            wait = 5 + spoken_text.text.count(" ") * 0.5
            time.sleep(wait)

    def _display_image(self, cache_dir, xkcd_number, img_nr, spoken_text):
        img = self._render(cache_dir, xkcd_number, img_nr, spoken_text)
        # TODO: show image on ePaper display
        # TODO: move pointer to the speaker

    def _render(self, cache_dir, xkcd_number, img_nr, spoken_text):
        cache_file_name = f"{xkcd_number}-{img_nr}-{spoken_text.speaker}.png"
        cache_file = cache_dir / cache_file_name
        if cache_file.exists():
            return cache_file.read_bytes()
        else:
            blob = renderer.render_xkcd_image(spoken_text.text)
            cache_file.write_bytes(blob)
            return blob

    def _show_break_picture(self, selected):
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers
        pass

    def _show_goodbye_picture(self):
        # TODO: implement something nice
        # TODO: show image on ePaper display
        # TODO: move pointer between speakers
        pass
