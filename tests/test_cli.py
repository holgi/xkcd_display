import pytest
import click
from click.testing import CliRunner
from unittest.mock import ANY, call


def test_xkcd_start_already_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "start")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["start"])

    assert result.exit_code == 0
    assert "already" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()
    assert XKCDDisplayService.start.call_count == 0


def test_xkcd_start_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "start")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["start"])

    assert result.exit_code == 0
    assert "starting" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.start.call_count == 1
    assert XKCDDisplayService.start.call_args == call(dialogs_directory=".")


def test_xkcd_stop_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "stop")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["stop"])

    assert result.exit_code == 0
    assert "stopping" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()
    assert XKCDDisplayService.stop.call_count == 1
    assert XKCDDisplayService.stop.call_args == call()



def test_xkcd_stop_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "stop")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["stop"])

    assert result.exit_code == 0
    assert "running" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()
    assert XKCDDisplayService.stop.call_count == 0


def test_xkcd_status_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)

    runner = CliRunner()
    result = runner.invoke(xkcd, ["status"])

    assert result.exit_code == 0
    assert "running" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()


def test_xkcd_status_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)

    runner = CliRunner()
    result = runner.invoke(xkcd, ["status"])

    assert result.exit_code == 0
    assert "stopped" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()


def test_xkcd_reload_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService
    import signal

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=True)
    mocker.patch.object(XKCDDisplayService, "send_signal")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["reload"])

    assert result.exit_code == 0
    assert "gracefully" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()
    assert XKCDDisplayService.send_signal.call_count == 1
    assert XKCDDisplayService.send_signal.call_args == call(signal.SIGHUP)


def test_xkcd_reload_not_running(mocker):
    from xkcd_display.cli import xkcd
    from xkcd_display.display import XKCDDisplayService

    mocker.patch.object(XKCDDisplayService, "is_running", return_value=False)
    mocker.patch.object(XKCDDisplayService, "send_signal")

    runner = CliRunner()
    result = runner.invoke(xkcd, ["reload"])

    assert result.exit_code == 0
    assert "not running" in result.output
    assert XKCDDisplayService.is_running.call_count == 1
    assert XKCDDisplayService.is_running.call_args == call()
    assert XKCDDisplayService.send_signal.call_count == 0


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

    assert Path.write_bytes.call_count == 2
    assert xkcd_display.renderer.render_xkcd_image.call_count == 2
    assert xkcd_display.renderer.render_xkcd_image.call_args_list == [
        call("yeah"), call("sigh")
        ]
    if showed:
        assert click.launch.call_count == 2
    else:
        assert click.launch.call_count == 0
    if slept:
        assert time.sleep.call_count == 1
        assert time.sleep.call_args == call(2)
    else:
        time.sleep.call_count == 0


def test_get_directory_context_manager_with_dir():
    from xkcd_display.cli import _get_directory_context_manager

    with _get_directory_context_manager("some thing") as result:
        assert result == "some thing"


def test_get_directory_context_manager_without_dir():
    from xkcd_display.cli import _get_directory_context_manager
    import tempfile

    result = _get_directory_context_manager(None)

    assert isinstance(result, tempfile.TemporaryDirectory)
