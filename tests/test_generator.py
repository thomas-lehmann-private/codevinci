"""Test of generator module."""

import xml.etree.ElementTree as ET
from pathlib import Path

from codevinci.generator import (
    GeneratorOptions,
    GeneratorOutputFormat,
    GraphvizClassGenerator,
)
from codevinci.parser import Parser

PACKAGE_PATH = "codevinci"


def test_graphviz_generator_for_svg():
    """Testing of graphviz generator for svg."""
    parser = Parser()
    moduleModels = parser.parse(PACKAGE_PATH)

    options = GeneratorOptions(GeneratorOutputFormat.SVG, str(Path.cwd()))
    generator = GraphvizClassGenerator(options)
    result = generator.generate(moduleModels)

    root = ET.fromstring(result.decode("utf-8"))
    assert root.tag.endswith("svg")


def test_graphviz_generator_for_svg_benchmark(benchmark):
    """Benchmark of graphviz generator for svg."""
    parser = Parser()
    moduleModels = parser.parse(PACKAGE_PATH)

    options = GeneratorOptions(GeneratorOutputFormat.SVG, str(Path.cwd()))
    generator = GraphvizClassGenerator(options)
    benchmark(generator.generate, moduleModels)


def test_graphviz_generator_for_source():
    """Testing of graphviz generator for source code."""
    parser = Parser()
    moduleModels = parser.parse(PACKAGE_PATH)

    options = GeneratorOptions(GeneratorOutputFormat.SOURCE, str(Path.cwd()))
    generator = GraphvizClassGenerator(options)
    result = generator.generate(moduleModels)

    assert result.find("cluster_parser") > 0
    assert result.find("ClassModel") > 0
