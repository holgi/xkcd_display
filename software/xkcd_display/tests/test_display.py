import pytest
import tempfile
import time

from pathlib import Path
from unittest.mock import ANY, call


EXAMPLE_DIALOG = """
    Cueball 1: You're flying! How?
    Megan: Python!
    Megan: I learned it last night!
    """


@pytest.fixture
def tmp_path():
    with tempfile.TemporaryDirectory() as tempdir:
        yield Path(tempdir)


def test_get_dialog_files(tmp_path):
    from xkcd_display.display import XKCDDisplayService

    names = ["ok.txt", "other.txt", ".hidden.txt", ".hidden", "wrong.md"]
    for name in names:
        file = tmp_path / name
        file.write_text(name)

    text_files = XKCDDisplayService()._get_dialog_files(tmp_path)

    assert set((tf.name for tf in text_files)) == {"ok.txt", "other.txt"}


def test_display_dialog(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService
    from xkcd_display.dialog import SpokenText

    mocker.patch.object(XKCDDisplayService, "_display_image")
    mocker.patch("time.sleep")
    dialog_file = tmp_path / "one_dialog.txt"
    dialog_file.write_text(EXAMPLE_DIALOG)

    XKCDDisplayService()._display_dialog(dialog_file)

    assert XKCDDisplayService._display_image.call_count == 3
    assert XKCDDisplayService._display_image.call_args_list == [
        call(SpokenText(speaker="cueball", text="You're flying! How?")),
        call(SpokenText(speaker="megan", text="Python!")),
        call(SpokenText(speaker="megan", text="I learned it last night!")),
    ]
    assert time.sleep.call_count == 3
    assert time.sleep.call_args_list == [call(6), call(5), call(7)]


def test_display_image(mocker):
    from xkcd_display.display import XKCDDisplayService
    from xkcd_display.dialog import SpokenText

    mocker.patch("xkcd_display.renderer.render_xkcd_image_as_pixels")

    XKCDDisplayService()._display_image(
        SpokenText(speaker="megan", text="*sigh*")
    )
    from xkcd_display.renderer import render_xkcd_image_as_pixels

    assert render_xkcd_image_as_pixels.call_count == 1
    assert render_xkcd_image_as_pixels.call_args == call("*sigh*")


def test_run_no_reload(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService
    import signal

    dialog_file = tmp_path / "123.txt"
    dialog_file.write_text(EXAMPLE_DIALOG)

    mocker.patch.object(
        XKCDDisplayService, "got_sigterm", side_effect=[False, False, True]
    )
    mocker.patch.object(
        XKCDDisplayService, "got_signal", side_effect=[False, False]
    )
    mocker.patch.object(XKCDDisplayService, "_display_dialog")
    mocker.patch.object(XKCDDisplayService, "_show_break_picture")
    mocker.patch.object(XKCDDisplayService, "_show_goodbye_picture")
    mocker.patch.object(
        XKCDDisplayService, "_get_dialog_files", return_value=[dialog_file]
    )

    XKCDDisplayService().run(tmp_path)

    assert XKCDDisplayService.got_sigterm.call_count == 3
    assert XKCDDisplayService.got_sigterm.call_args_list == [
        call(),
        call(),
        call(),
    ]
    assert XKCDDisplayService.got_signal.call_count == 2
    assert XKCDDisplayService.got_signal.call_args_list == [
        call(signal.SIGHUP, clear=True),
        call(signal.SIGHUP, clear=True),
    ]
    assert XKCDDisplayService._display_dialog.call_count == 2
    assert XKCDDisplayService._display_dialog.call_args_list == [
        call(dialog_file),
        call(dialog_file),
    ]
    assert XKCDDisplayService._show_break_picture.call_count == 2
    assert XKCDDisplayService._show_break_picture.call_args_list == [
        call(None, dialog_file),
        call(dialog_file, dialog_file),
    ]
    assert XKCDDisplayService._show_goodbye_picture.call_count == 1
    assert XKCDDisplayService._show_goodbye_picture.call_args == call()
    assert XKCDDisplayService._get_dialog_files.call_count == 1
    assert XKCDDisplayService._get_dialog_files.call_args == call(tmp_path)


def test_run_with_reload(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService
    import signal

    dialog_file = tmp_path / "123.txt"
    dialog_file.write_text(EXAMPLE_DIALOG)

    mocker.patch.object(
        XKCDDisplayService, "got_sigterm", side_effect=[False, False, True]
    )
    mocker.patch.object(
        XKCDDisplayService, "got_signal", side_effect=[True, False]
    )
    mocker.patch.object(XKCDDisplayService, "_display_dialog")
    mocker.patch.object(XKCDDisplayService, "_show_break_picture")
    mocker.patch.object(XKCDDisplayService, "_show_goodbye_picture")
    mocker.patch.object(
        XKCDDisplayService, "_get_dialog_files", return_value=[dialog_file]
    )

    XKCDDisplayService().run(tmp_path)

    assert XKCDDisplayService.got_sigterm.call_count == 3
    assert XKCDDisplayService.got_sigterm.call_args_list == [
        call(),
        call(),
        call(),
    ]
    assert XKCDDisplayService.got_signal.call_count == 2
    assert XKCDDisplayService.got_signal.call_args_list == [
        call(signal.SIGHUP, clear=True),
        call(signal.SIGHUP, clear=True),
    ]
    assert XKCDDisplayService._display_dialog.call_count == 2
    assert XKCDDisplayService._display_dialog.call_args_list == [
        call(dialog_file),
        call(dialog_file),
    ]
    assert XKCDDisplayService._show_break_picture.call_count == 2
    assert XKCDDisplayService._show_break_picture.call_args_list == [
        call(None, dialog_file),
        call(dialog_file, dialog_file),
    ]
    assert XKCDDisplayService._show_goodbye_picture.call_count == 1
    assert XKCDDisplayService._show_goodbye_picture.call_args == call()
    assert XKCDDisplayService._get_dialog_files.call_count == 2
    assert XKCDDisplayService._get_dialog_files.call_args_list == [
        call(tmp_path),
        call(tmp_path),
    ]
