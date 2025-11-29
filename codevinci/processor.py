"""Module processor."""

from logging import getLogger, Logger
import os
from typing import Any

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
        self.__logger: Logger = getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )
        self.__options = options

    def process(self, path: str) -> None:
        """
        Parse all files.

        Args:
            path: start path to search all Python files.
        """
        parser = Parser()
        module_models = parser.parse(path)
        generator = GraphvizClassGenerator(self.__options)
        self.__write_content(generator.generate(module_models))

    def process_string(self, code: str) -> None:
        """
        Parse code.

        Args:
            code: Python code as text or from one file.
        """
        parser = Parser()
        module_models = parser.parse_string(code)
        generator = GraphvizClassGenerator(self.__options)
        self.__write_content(generator.generate(module_models))

    def __write_content(self, content: Any) -> None:
        """Write content to file depending on output format."""
        match self.__options.get_output_format():
            case GeneratorOutputFormat.SVG:
                file = os.path.join(self.__options.get_output_path(), "design.svg")
                self.__logger.info(f"Writing diagram as {file}")
                with open(file, "wb") as handle:
                    handle.write(content)
            case GeneratorOutputFormat.PNG:
                file = os.path.join(self.__options.get_output_path(), "design.png")
                self.__logger.info(f"Writing diagram as {file}")
                with open(file, "wb") as handle:
                    handle.write(content)
            case GeneratorOutputFormat.SOURCE:
                file = os.path.join(self.__options.get_output_path(), "design.source")
                self.__logger.info(f"Writing diagram as {file}")
                with open(file, "w") as handle:
                    handle.write(content)
