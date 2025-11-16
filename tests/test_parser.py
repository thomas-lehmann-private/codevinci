"""Test of parser."""

from codevinci.parser import Parser


def test_parser():
    """Testing of Parser."""
    parser = Parser()
    moduleModels = parser.parse("codevinci")
    assert len(moduleModels) > 0

    # probe test
    found_classes = [
        classModel
        for moduleModel in moduleModels
        for classModel in moduleModel.get_classes()
        if classModel.get_name() == "Parser"
    ]

    assert len(found_classes) == 1
    assert found_classes[0].get_name() == "Parser"
    assert len(found_classes[0].get_methods()) > 0
