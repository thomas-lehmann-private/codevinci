"""Module tools.

The MIT License

Copyright 2025 Thomas Lehmann.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import ast
from typing import Any, Generator, Tuple

from codevinci.files import Files
from codevinci.parser.annotation import AnnotationParser


class ParserTools:
    """Basic helper for parsing ast."""

    @staticmethod
    def from_file(path: str) -> Any:
        """Parse AST for a given file.

        Args:
            path: path and name of Python file to get ast tree from.

        Example:
            >>> tree = ParserTools.from_file(__file__)
            >>> for node in ast.walk(tree):
            ...     if isinstance(node, ast.ClassDef):
            ...         print(node.name)
            ParserTools
        """
        with open(path, "r", encoding="utf-8") as handle:
            return ast.parse(handle.read(), filename=path)

    @staticmethod
    def find_all_classes(path: str) -> Generator[Tuple[str, ast.ClassDef], None, None]:
        """Find all classes for given package path.

        Args:
            path: path to start searching for Python files (modules)

        Returns:
            Generator with tuple of path and filename of module and
            the ast node for the found class.

        Example:
            >>> nodes = list(ParserTools.find_all_classes('codevinci'))
            >>> names = [node.name for _, node in nodes]
            >>> assert 'ParserTools' in names
        """
        for file in Files.scan(path):
            tree = ParserTools.from_file(file)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    yield file, node

    @staticmethod
    def find_all_methods(node: ast.ClassDef) -> Generator[ast.FunctionDef, None, None]:
        """Find all methods for an AST class node."""
        for child_node in ast.iter_child_nodes(node):
            if isinstance(child_node, ast.FunctionDef):
                yield child_node

    @staticmethod
    def find_all_bases(node: ast.ClassDef) -> Generator[str, None, None]:
        """Find all base classes (name) for given AST class node."""
        for base in node.bases:
            if isinstance(base, ast.Name):
                yield base.id

    @staticmethod
    def find_all_method_arguments(
        node: ast.FunctionDef,
    ) -> Generator[Tuple[str, str, set[str]], None, None]:
        """find all method arguments (including annotations)."""
        for child_node in ast.iter_child_nodes(node.args):
            if isinstance(child_node, ast.arg):
                argument_name: str = child_node.arg
                argument_type: str = ""
                names: list[str] = []

                if child_node.annotation:
                    argument_type, names = AnnotationParser.resolve(
                        child_node.annotation
                    )

                yield argument_name, argument_type, set(names)

    @staticmethod
    def find_method_return_type(node: ast.FunctionDef) -> Tuple[str, list[str]]:
        """Get Methods return type."""
        return_type: str = ""
        names: list[str] = []

        if node.returns:
            return_type, names = AnnotationParser.resolve(node.returns)

        return return_type, names

    @staticmethod
    def find_all_instance_attributes(node: ast.FunctionDef):
        """Provide all instance attributes of a class."""
        if node.name == "__init__":
            for child_node in ast.iter_child_nodes(node):
                if not isinstance(child_node, ast.AnnAssign):
                    continue
                if not isinstance(child_node.target, ast.Attribute):
                    continue
                if not isinstance(child_node.target.value, ast.Name):
                    continue
                if not child_node.target.value.id == "self":
                    continue

                attribute_name: str = child_node.target.attr
                attribute_type: str = ""
                names: list[str] = []

                if child_node.annotation:
                    attribute_type, names = AnnotationParser.resolve(
                        child_node.annotation
                    )

                yield attribute_name, attribute_type, names

    @staticmethod
    def is_abstract_method(node: ast.FunctionDef) -> bool:
        """Checking given method to be an abstract method."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "abstractmethod":
                return True
        return False

    @staticmethod
    def is_static_method(node: ast.FunctionDef) -> bool:
        """Checking given method to be an static method."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "staticmethod":
                return True
        return False
