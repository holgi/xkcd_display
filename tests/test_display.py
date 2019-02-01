import pytest
import tempfile
import time

from pathlib import Path


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


def test_clear_cache(tmp_path):
    from xkcd_display.display import XKCDDisplayService

    for i in range(1, 5):
        file = tmp_path / str(i)
        file.write_text("hello")

    XKCDDisplayService()._clear_cache(tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_display_dialog(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "_display_image")
    mocker.patch("time.sleep")
    dialog_file = tmp_path / "one_dialog.txt"
    dialog_file.write_text(EXAMPLE_DIALOG)

    XKCDDisplayService()._display_dialog(tmp_path, dialog_file)

    assert XKCDDisplayService._display_image.call_count == 3
    assert time.sleep.call_count == 3


def test_display_image(mocker):
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "_render")

    XKCDDisplayService()._display_image("cache_dir", 12, 3, "*sigh")

    XKCDDisplayService._render.assert_called_once_with(
        "cache_dir", 12, 3, "*sigh"
    )


def test_render_cached(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService
    from xkcd_display.dialog import SpokenText

    mocker.patch(
        "xkcd_display.renderer.render_xkcd_image", return_value="image"
    )
    mocker.patch.object(Path, "read_bytes", return_value="cache")
    mocker.patch.object(Path, "write_bytes")
    mocker.patch.object(Path, "exists", return_value=True)

    result = XKCDDisplayService()._render(tmp_path, 12, 3, SpokenText("", ""))

    assert result == "cache"
    Path.exists.assert_called_once()
    Path.read_bytes.assert_called_once()
    Path.write_bytes.assert_not_called()


def test_render_not_cached(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService
    from xkcd_display.dialog import SpokenText

    mocker.patch(
        "xkcd_display.renderer.render_xkcd_image", return_value="image"
    )
    mocker.patch.object(Path, "read_bytes", return_value="cache")
    mocker.patch.object(Path, "write_bytes")
    mocker.patch.object(Path, "exists", return_value=False)

    result = XKCDDisplayService()._render(tmp_path, 12, 3, SpokenText("", ""))

    assert result == "image"
    Path.exists.assert_called_once()
    Path.read_bytes.assert_not_called()
    Path.write_bytes.assert_called_once()


def test_run_no_reload(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService

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
    mocker.patch.object(XKCDDisplayService, "_clear_cache")
    mocker.patch.object(XKCDDisplayService, "_get_dialog_files", return_value=[dialog_file])

    XKCDDisplayService().run(tmp_path)

    assert XKCDDisplayService.got_sigterm.call_count == 3
    assert XKCDDisplayService.got_signal.call_count == 2
    assert XKCDDisplayService._display_dialog.call_count == 2
    assert XKCDDisplayService._show_break_picture.call_count == 2
    XKCDDisplayService._show_goodbye_picture.assert_called_once()
    XKCDDisplayService._get_dialog_files.assert_called_once()
    XKCDDisplayService._clear_cache.assert_not_called()


def test_run_with_reload(tmp_path, mocker):
    from xkcd_display.display import XKCDDisplayService

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
    mocker.patch.object(XKCDDisplayService, "_clear_cache")
    mocker.patch.object(XKCDDisplayService, "_get_dialog_files", return_value=[dialog_file])

    XKCDDisplayService().run(tmp_path)

    assert XKCDDisplayService.got_sigterm.call_count == 3
    assert XKCDDisplayService.got_signal.call_count == 2
    assert XKCDDisplayService._display_dialog.call_count == 2
    assert XKCDDisplayService._show_break_picture.call_count == 2
    assert XKCDDisplayService._get_dialog_files.call_count == 2
    XKCDDisplayService._show_goodbye_picture.assert_called_once()
    XKCDDisplayService._clear_cache.assert_called_once()


