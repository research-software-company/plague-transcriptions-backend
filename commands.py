import click
from flask.cli import with_appcontext
from flask.globals import current_app


@click.command()
@with_appcontext
def ingest():
    print('Import is here', current_app.config)


def init_app(app):
    app.cli.add_command(ingest)
