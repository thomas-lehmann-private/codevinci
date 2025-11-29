"""Testing of script."""

import builtins
from unittest.mock import mock_open
import xml.etree.ElementTree as ET

from codevinci.script import real_design
from codevinci.generator import GeneratorOutputFormat


def test_script_basics(monkeypatch):
    """Testing of basic codevinci script usage."""
    written_data = {}

    real_open = builtins.open

    def fake_open(path, mode, *args, **kwargs):
        """Fake of 'open' function."""
        if path.find("docs") >= 0 and "w" in mode:
            mocked = mock_open()
            handle = mocked()

            def fake_write(data):
                """Fake the write of data."""
                written_data["data"] = data
                return len(data)

            handle.write = fake_write
            return handle

        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    real_design(
        **{
            "output_path": "docs",
            "output_format": GeneratorOutputFormat.SVG,
            "package_path": "codevinci",
            "color": ["header:#00f000"],
            "aggregated_dependencies": False,
            "stdin": False,
        }
    )

    result = written_data.get("data")

    root = ET.fromstring(result.decode("utf-8"))
    assert root.tag.endswith("svg")
