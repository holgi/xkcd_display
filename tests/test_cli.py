import pytest
import click


from click.testing import CliRunner


def test_xkcd_start_already_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "start")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["start"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.start.assert_not_called()
    assert result.exit_code == 0
    assert "already" in result.output


def test_xkcd_start_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "start")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["start"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.start.assert_called_once_with(dialogs_directory=".")
    assert result.exit_code == 0
    assert "starting" in result.output


def test_xkcd_stop_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "stop")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["stop"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.stop.assert_called_once()
    assert result.exit_code == 0
    assert "stopping" in result.output


def test_xkcd_stop_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "stop")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["stop"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.stop.assert_not_called()
    assert result.exit_code == 0
    assert "running" in result.output


def test_xkcd_status_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)

    runner = CliRunner()
    result = runner.invoke(xkcd, ["status"])

    XKCDDisplayService.is_running.assert_called_once()
    assert result.exit_code == 0
    assert "running" in result.output


def test_xkcd_status_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)

    runner = CliRunner()
    result = runner.invoke(xkcd, ["status"])

    XKCDDisplayService.is_running.assert_called_once()
    assert result.exit_code == 0
    assert "stopped" in result.output


def test_xkcd_reload_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService
    import signal

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "send_signal")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["reload"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.send_signal.assert_called_once_with(signal.SIGHUP)
    assert result.exit_code == 0
    assert "gracefully" in result.output


def test_xkcd_reload_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "send_signal")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["reload"])

    XKCDDisplayService.is_running.assert_called_once()
    XKCDDisplayService.send_signal.assert_not_called()
    assert result.exit_code == 0
    assert "not running" in result.output


@pytest.mark.parametrize(
    "cli_args, showed, slept",
    [
        (["text.txt"], True, True),
        (["--show", "text.txt"], True, True),
        (["--show", "-o", "/tmp", "text.txt"], True, False),
        (["-o", "/tmp", "text.txt"], False, False),
    ],
)
def test_xkcdtest_show_no_outdir(cli_args, showed, slept, mocker):
    from xkcd_display.cli import xkcdtest
    import xkcd_display.renderer
    from pathlib import Path
    import time

    mocker.patch.object(Path, "write_bytes")
    mocker.patch.object(
        xkcd_display.renderer, "render_xkcd_image", return_value=b"1"
    )
    mocker.patch.object(click, "launch")
    mocker.patch("time.sleep")

    runner = CliRunner()
    with runner.isolated_filesystem():
        with open("text.txt", "w") as f:
            f.write("m:yeah\nc:sigh")
        result = runner.invoke(xkcdtest, cli_args)
        print("OUTPUT:")
        print(result.output)
        assert result.exit_code == 0

    Path.write_bytes.assert_called()
    xkcd_display.renderer.render_xkcd_image.assert_called()
    if showed:
        click.launch.assert_called()
    else:
        click.launch.assert_not_called()
    if slept:
        time.sleep.assert_called_once_with(2)
    else:
        time.sleep.assert_not_called()


def test_get_directory_context_manager_with_dir():
    from xkcd_display.cli import _get_directory_context_manager

    with _get_directory_context_manager("some thing") as result:
        assert result == "some thing"


def test_get_directory_context_manager_without_dir():
    from xkcd_display.cli import _get_directory_context_manager
    import tempfile

    result = _get_directory_context_manager(None)
    assert isinstance(result, tempfile.TemporaryDirectory)
