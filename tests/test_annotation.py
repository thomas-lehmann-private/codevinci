"""Module test_annotation."""

import ast
from typing import Tuple

from codevinci.parser import AnnotationParser, ParserTools


def test_parsing_simple_return_type():
    """Test parsing of a simple return type."""

    def get_simple_value() -> str:
        """Provide simple value."""
        return "hello world"

    tree = ParserTools.from_file(__file__)
    return_type: str = ""
    names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_simple_value":
                return_type, names = AnnotationParser.resolve(node.returns)
                break
    assert return_type == "str"
    assert names == ["str"]


def test_parsing_simple_return_type_as_constant():
    """Test parsing of a simple return type as constant."""

    def get_simple_value_as_constant() -> "str":
        """Provide simple value."""
        return "hello world"

    tree = ParserTools.from_file(__file__)
    return_type: str = ""
    names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_simple_value_as_constant":
                return_type, names = AnnotationParser.resolve(node.returns)
                break
    assert return_type == "str"
    assert names == ["str"]


def test_parsing_simple_return_type_as_list():
    """Test parsing of a simple return type as list."""

    def get_simple_value_as_list() -> list[str]:
        """Provide simple value as list."""
        return ["hello world"]

    tree = ParserTools.from_file(__file__)
    return_type: str = ""
    names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_simple_value_as_list":
                return_type, names = AnnotationParser.resolve(node.returns)
                break
    assert return_type == "list[str]"
    assert names == ["list", "str"]


def test_parsing_simple_return_type_as_dict():
    """Test parsing of a simple return type as dict."""

    def get_simple_value_as_dict() -> dict[str, str]:
        """Provide simple value as dict."""
        return {"message": "hello world"}

    tree = ParserTools.from_file(__file__)
    return_type: str = ""
    names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_simple_value_as_dict":
                return_type, names = AnnotationParser.resolve(node.returns)
                break
    assert return_type == "dict[str, str]"
    assert names == ["dict", "str", "str"]


def test_parsing_simple_return_type_as_tuple():
    """Test parsing of a simple return type as tuple."""

    def get_simple_value_as_tuple() -> Tuple[str, str]:
        """Provide simple value as dict."""
        return "hello world 1", "hello world 2"

    tree = ParserTools.from_file(__file__)
    return_type: str = ""
    names: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name == "get_simple_value_as_tuple":
                return_type, names = AnnotationParser.resolve(node.returns)
                break
    assert return_type == "Tuple[str, str]"
    assert names == ["Tuple", "str", "str"]
