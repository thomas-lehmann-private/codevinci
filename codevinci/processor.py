"""Module processor."""

from logging import getLogger, Logger
import os

from codevinci.parser import Parser
from codevinci.generator import (
    GeneratorOptions,
    GeneratorOutputFormat,
    GraphvizClassGenerator,
)


class Processor:
    """Processor for parsing files and visualizing them."""

    def __init__(self, options: GeneratorOptions):
        """Initialize processor."""
        self.__logger: Logger = getLogger(__name__)
        self.__options = options

    def process(self, path: str) -> None:
        """
        Parse all files.

        Args:
            path: start path to search all Python files.
        """
        parser = Parser()
        classModels = parser.parse(path)
        generator = GraphvizClassGenerator(self.__options)
        content = generator.generate(classModels)

        match self.__options.get_output_format():
            case GeneratorOutputFormat.SVG:
                file = os.path.join(self.__options.get_output_path(), "classes.svg")
                with open(file, "wb") as handle:
                    handle.write(content)
            case GeneratorOutputFormat.PNG:
                file = os.path.join(self.__options.get_output_path(), "classes.png")
                with open(file, "wb") as handle:
                    handle.write(content)
            case GeneratorOutputFormat.SOURCE:
                file = os.path.join(self.__options.get_output_path(), "classes.source")
                with open(file, "w") as handle:
                    handle.write(content)
