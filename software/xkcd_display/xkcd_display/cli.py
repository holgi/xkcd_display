""" Command line interface for the xkcd display service """

import click
import contextlib
import signal
import tempfile
import time

from pathlib import Path

from . import dialog
from . import renderer
from . import display


@click.group()
def xkcd():
    """ controll the dedicated xkcd display"""


@xkcd.command(short_help="start the xkcd display service")
def start():
    """ starts the xkcd display service

    This will start to render dialogs and show them on the display
    """
    xd = display.XKCDDisplayService("/Users/holgerfrey/Developer/xkcd_dialogs")
    if xd.is_running():
        click.echo("xkcd service already running")
    else:
        click.echo("starting xkcd service")
        xd.start()


@xkcd.command(short_help="stop the xkcd display service")
def stop():
    """ stop the xkcd display service

    This will stop the display service after the last panel of the current
    dialog was displayed.
    """
    xd = display.XKCDDisplayService()
    if xd.is_running():
        click.echo("stopping xkcd servie")
        xd.stop()
    else:
        click.echo("xkcd service not running")


@xkcd.command(short_help="is the xkcd display service running?")
def status():
    """ reports if the xkcd display service is running """
    xd = display.XKCDDisplayService()
    if xd.is_running():
        click.echo(click.style("xkcd service is running.", fg="green"))
    else:
        click.echo(click.style("xkcd service is stopped.", fg="red"))


@xkcd.command(short_help="gracefully reload the xkcd display service")
def reload():
    """ will gracefully reload the xkcd display service

    The configuration and dialogs are reloaded after the current dialog is
    finished. Useful if new dialogs are added.
    """
    xd = display.XKCDDisplayService()
    if xd.is_running():
        click.echo("gracefully reloading changes")
        xd.send_signal(signal.SIGHUP)
    else:
        click.echo("xkcd service not running")


@click.command()
@click.option(
    "--show", is_flag=True, help="open the generated images [default: don't]"
)
@click.option(
    "--outdir",
    "-o",
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=True
    ),
    help="output directory",
)
@click.argument(
    "dialogfile",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True
    ),
)
def xkcdtest(show, outdir, dialogfile):
    """ will render one dialog to panel images in a directory

    Use this after a new dialog has been added before using the display service
    to show it. Sometimes adjustments to the dialog have to be made...

    If now output directory is set, the images are rendered to a temporary
    directory and are shown even if --show is not selected.

    :param click.Context context: command line context
    :param bool show: show the image in the default image viewer
    :param str outdir: where to save the images
    :param str diaglogfile: path to the dialog text file
    """

    if not outdir:
        show = True

    dialog_path = Path(dialogfile)
    raw_transcript = dialog.parse_dialog(dialog_path.read_text())
    transcript = dialog.adjust_narrators(raw_transcript)

    context_manager = _get_directory_context_manager(outdir)

    with context_manager as output_dir_name:
        output_dir = Path(output_dir_name)
        for i, spoken_text in enumerate(transcript):
            blob = renderer.render_xkcd_image_as_gif(spoken_text.text)
            panel = i + 1
            image_file = (
                output_dir
                / f"{dialog_path.stem}-{panel:>02}-{spoken_text.speaker}.gif"
            )
            image_file.write_bytes(blob)
            if show:
                click.launch(str(image_file))
        # added some waiting time if a temporary directory is used.
        # It often happens, that the showing the image takes some time and
        # the temporary directory might be removed in the meanwhile
        if not outdir:
            time.sleep(2)


def _get_directory_context_manager(outdir):
    """ returns a context manager for the output directory

    This unifies the interface for a temporary directory and a normal one

    :param str outdir: path to the output directory or None
    """
    if outdir:
        return contextlib.nullcontext(outdir)
    else:
        return tempfile.TemporaryDirectory()
