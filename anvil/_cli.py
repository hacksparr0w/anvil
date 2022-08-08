from pathlib import Path

import click

from .core import install, load_blueprint


DEFAULT_BLUEPRINT_DIRECTORY = (
    Path(__file__).parent / "../anvil_blueprints"
).resolve()

PACKAGE_DIRECTORY_NAME = "packages"


@click.command("install")
@click.argument("name")
def install_command(name: str) -> None:
    package_directory = Path.cwd() / PACKAGE_DIRECTORY_NAME

    install(DEFAULT_BLUEPRINT_DIRECTORY, package_directory, name)


@click.command("list")
def list_command() -> None:
    paths = []

    for path in DEFAULT_BLUEPRINT_DIRECTORY.iterdir():
        if path.is_file() and path.name.endswith(".py"):
            paths.append(path)

    if len(paths) == 0:
        click.echo("No blueprints available.")
        return

    click.echo("Available blueprints:")

    for path in paths:
        blueprint = load_blueprint(path)

        click.echo(f" - {blueprint.name()} ({blueprint.source().url})")

    click.echo("")
    click.echo(f"Listed {len(paths)} blueprints.")


@click.group()
def cli():
    pass


cli.add_command(install_command)
cli.add_command(list_command)
