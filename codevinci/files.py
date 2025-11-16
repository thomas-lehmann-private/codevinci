"""Module files."""

import os
from typing import Generator


class Files:
    """Tool class for file operations."""

    @staticmethod
    def scan(path: str) -> Generator[str, None, None]:
        """Provide all python files under given path."""
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".py") and not (file == "__init__.py"):
                    full_name = os.path.join(root, file)
                    yield full_name
