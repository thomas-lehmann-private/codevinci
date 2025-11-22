"""Testing of processor class."""

import builtins
from unittest.mock import mock_open
import xml.etree.ElementTree as ET

from codevinci.parser import Parser
from codevinci.processor import Processor
from codevinci.generator import (
    GeneratorOptions,
    GeneratorOutputFormat,
    GraphvizClassGenerator,
)

import pytest


@pytest.mark.parametrize(
    "fmt,expected_filename,write_mode",
    [
        (GeneratorOutputFormat.SVG, "design.svg", "wb"),
        (GeneratorOutputFormat.PNG, "design.png", "wb"),
        (GeneratorOutputFormat.SOURCE, "design.source", "w"),
    ],
)
def test_generator_with_graphviz_check_write(
    monkeypatch, fmt, expected_filename, write_mode
):
    """Testing of processor usage with focus on writing content."""
    fake_content = b"<svg></svg>"
    monkeypatch.setattr(
        GraphvizClassGenerator, "generate", lambda self, _: fake_content
    )
    monkeypatch.setattr(Parser, "parse", lambda self, _: [])

    mocked_open = mock_open()
    monkeypatch.setattr("builtins.open", mocked_open)

    options = GeneratorOptions(fmt, ".")
    processor = Processor(options)
    processor.process("codevinci")

    mocked_open.assert_called_once_with("./" + expected_filename, write_mode)
    mocked_open().write.assert_called_once_with(fake_content)


def test_generator_with_graphviz_for_svg(monkeypatch):
    """Testing of processor usage."""
    written_data = {}

    real_open = builtins.open

    def fake_open(*args, **kwargs):
        """A faked open for the processor itself."""
        mode = args[1] if len(args) > 1 else kwargs.get("mode", "r")

        # 👉 the processor is the only one that does write files
        if "w" in mode or "b" in mode:
            mocked_open = mock_open()
            handle = mocked_open()
            original_write = handle.write

            def fake_write(data):
                """Fake of write."""
                written_data["data"] = data
                return original_write(data)

            handle.write = fake_write
            return handle

        # 👉 allow all other 'open' to be real (example: Parser)
        return real_open(*args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    options = GeneratorOptions(GeneratorOutputFormat.SVG, ".")
    processor = Processor(options)
    processor.process("codevinci")

    result = written_data.get("data")
    root = ET.fromstring(result.decode("utf-8"))
    assert root.tag.endswith("svg")
