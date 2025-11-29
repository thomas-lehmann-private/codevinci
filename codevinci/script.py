"""Script for generating a class diagram."""

import logging
import os
from pathlib import Path

from codevinci.processor import Processor
from codevinci.generator import GeneratorOptions, GeneratorOutputFormat

import click


def print_version(ctx, param, value):
    """Print tool version."""
    if not value or ctx.resilient_parsing:
        return
    click.echo("codevinci v1.0.0")
    ctx.exit()


@click.group
@click.option(
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="print version of this tool (and library)",
)
def main():
    """
    CodeVinci is a Python source code analysis tool designed to generate clear, expressive diagrams of your project’s internal structure. By parsing Python modules, it extracts and visualizes:

    - Module relationships\n
    - Class hierarchies\n
    - Instance attributes\n
    - Methods and their arguments\n
    - Inter-module and inter-class dependencies\n

    The goal is to provide a powerful, modern alternative to tools like
    pdoc and pyreverse, with rich visual output, color-coded information
    layers, and an emphasis on intuitive understanding of complex codebases.

    In the future, CodeVinci will also support HTML documentation generation,
    using the same analysis engine to produce cohesive, navigable documentation
    for entire Python projects.
    """


def initialize_logging():
    """Initialize logging."""
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(filename="codevinci.log", format=format, level=logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def real_design(**options):
    """Implement the design part of the tool."""
    initialize_logging()
    # ensure that path does exist
    os.makedirs(options["output_path"], exist_ok=True)

    generator_options = GeneratorOptions(
        options["output_format"], options["output_path"]
    )

    generator_options.set_aggregated_dependencies(options["aggregated_dependencies"])

    color_config = generator_options.get_color_config()
    for entry in options["color"]:
        if ":" not in entry:
            raise click.UsageError("Use --color key:#rrggbb")
        key, value = entry.split(":", 1)
        color_config.apply_override(key.strip(), value.strip())

    processor = Processor(generator_options)
    processor.process(options["package_path"])


@main.command("design")
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
@click.option(
    "--aggregated-dependencies",
    is_flag=True,
    help="reduce dependencies to class to class",
)
def design(**options):
    """Generate diagram from Python code."""
    real_design(**options)


if __name__ == "__main__":
    main()
