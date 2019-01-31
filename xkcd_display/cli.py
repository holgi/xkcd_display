import click

@click.group()
def cli():
    pass

@cli.command()
def start():
    click.echo("starting xkcd service")

@cli.command()
def stop():
    click.echo("stopping xkcd servie")

@cli.command()
def status():
    click.echo("reporting xkcd service status")

@cli.command()
def reload():
    click.echo("gracefully reloading changes")

@cli.command()
def render():
    click.echo("test-renders one dialog")
