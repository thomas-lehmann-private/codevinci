"""Script for generating a class diagram."""

import logging
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


# TODO: --aggregated-dependencies umsetzen
# TODO: Return Type von Methoden ergänzen (inklusive Dependencies)
# TODO: Benchmark der Generierung des Digrams je Ausgabeformat (https://pytest-benchmark.readthedocs.io/en/latest/)
# TODO: Mkdocs für übergreifende Dokumentation
# TODO: Installer (wheel); schauen wie das mit dem Script funktioniert.
# TODO: (final) Github Repository (Workflows)
# TODO: Im PYPI veröffentlichen
# TODO: statische Methoden als Kursiv darstellen
# TODO: abstrakte Methoden anders darstellen (noch zu prüfen was geeignet ist)
# TODO: (nice to have) Darstelling von Komplexität auf Ebene der Klasse und auf Ebene der Methode


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
    default=str(Path.cwd()),
    help="where to write the classes diagramm to (default: current path)",
)
def main(**options):
    """Application entry point."""
    initialize_logging()
    generator_options = GeneratorOptions(
        options["output_format"], options["output_path"]
    )
    processor = Processor(generator_options)
    processor.process(options["package_path"])


if __name__ == "__main__":
    main()
