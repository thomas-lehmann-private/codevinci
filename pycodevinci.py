"""Script for generating a class diagram."""

import logging
import os
from pathlib import Path

from codevinci.processor import Processor
from codevinci.generator import GeneratorOptions, GeneratorOutputFormat

import click


def initialize_logging():
    """Initialize logging."""
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename="codevinci.log", format=format, level=logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


# TODO: Installer (wheel); schauen wie das mit dem Script funktioniert.


@click.command()
@click.option("--package-path", help="root path to the packages")
@click.option(
    "--output-format",
    type=click.Choice(GeneratorOutputFormat),
    default=GeneratorOutputFormat.SVG,
    help="defines output format (default: SVG)",
)
@click.option(
    "--output-path",
    type=str,
    default=str(Path.joinpath(Path.cwd(), "docs")),
    help="where to write the classes diagramm to (default: current path)",
)
@click.option(
    "--color",
    multiple=True,
    help="Override colors, e.g. --color <name>:#ffeeaa (read doc)",
)
def main(**options):
    """Application entry point."""
    initialize_logging()
    # ensure that path does exist
    os.makedirs(options["output_path"], exist_ok=True)

    generator_options = GeneratorOptions(
        options["output_format"], options["output_path"]
    )

    color_config = generator_options.get_color_config()
    for entry in options["color"]:
        if ":" not in entry:
            raise click.UsageError("Use --color key:#rrggbb")
        key, value = entry.split(":", 1)
        color_config.apply_override(key.strip(), value.strip())

    processor = Processor(generator_options)
    processor.process(options["package_path"])


if __name__ == "__main__":
    main()
