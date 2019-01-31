""" Command line interface for the xkcd display service """

import click
import contextlib
import tempfile
import time

from pathlib import Path

from . import dialog
from . import renderer


@click.group()
def cli():
    """ controll the dedicated xkcd display """
    pass


@cli.command(short_help="start the xkcd display service")
def start():
    """ starts the xkcd display service

    This will start to render dialogs and show them on the display
    """
    click.echo("starting xkcd service")


@cli.command(short_help="stop the xkcd display service")
def stop():
    """ stop the xkcd display service

    This will stop the display service after the last panel of the current
    dialog was displayed.
    """
    click.echo("stopping xkcd servie")


@cli.command(short_help="is the xkcd display service running?")
def status():
    """ reports if the xkcd display service is running """
    click.echo("reporting xkcd service status")


@cli.command(short_help="gracefully reload the xkcd display service")
def reload():
    """ will gracefully reload the xkcd display service

    The configuration and dialogs are reloaded after the current dialog is
    finished. Useful if new dialogs are added.
    """
    click.echo("gracefully reloading changes")


@cli.command(short_help="test render one dialog")
@click.option(
    "--show",
    is_flag=True,
    help="open the generated images [default: don't]",
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
def render(show, outdir, dialogfile):
    """ will render one dialog to panel images in a directory

    Use this after a new dialog has been added before using the display service
    to show it. Sometimes adjustments to the dialog have to be made...

    If now output directory is set, the images are rendered to a temporary
    directory and are shown even if --quite is selected.
    """
    if outdir:
        context_manager = contextlib.nullcontext(outdir)
    else:
        context_manager = tempfile.TemporaryDirectory()
        show = True

    dialog_path = Path(dialogfile)
    raw_transcript = dialog.parse_dialog(dialog_path.read_text())
    transcript = dialog.adjust_narrators(raw_transcript)

    with context_manager as output_dir_name:
        output_dir = Path(output_dir_name)
        for i, spoken_text in enumerate(transcript):
            blob = renderer.render_xkcd_image(spoken_text.text)
            panel = i + 1
            image_file = (
                output_dir
                / f"{dialog_path.stem}-{panel:>02}-{spoken_text.speaker}.png"
            )
            image_file.write_bytes(blob)
            if show:
                click.launch(str(image_file))
        # added some waiting time if a temporary directory is used.
        # It often happens, that the showing the image takes some time and
        # the temporary directory might be removed in the meanwhile
        if not outdir:
            time.sleep(2)
