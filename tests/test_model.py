""" "Test of module classes."""

from codevinci.parser import (
    ClassModel,
    DependencyModel,
    DependencyType,
    MethodModel,
    MethodType,
    ModelType,
    ModuleModel,
    Origin,
)

import pytest


def test_class_model_basics():
    """Test basics of class ClassModel."""
    model = ClassModel("test")
    assert model.get_name() == "test"
    assert model.get_model_type() == ModelType.CLASS
    assert model.get_origin() == Origin.PACKAGE
    assert len(model.get_methods()) == 0
    assert len(model.get_bases()) == 0
    assert not model.has_methods()
    assert str(model) == "ClassModel(test)"

    model = ClassModel("test", Origin.BUILTIN)
    assert model.get_origin() == Origin.BUILTIN


def test_class_model_with_one_methods():
    """Test of ClassModel with one method."""
    model = ClassModel("test")
    method = MethodModel("get_value")
    model.add_method(method)
    assert model.get_name() == "test"
    assert len(model.get_methods()) == 1
    assert model.has_methods()
    assert model.get_methods()[0] == method


def test_method_model_basics():
    """Test of MethodModel."""
    model = MethodModel("test")
    assert model.get_name() == "test"
    assert model.get_model_type() == ModelType.METHOD
    assert model.get_origin() == Origin.CLASS
    assert model.get_method_type() == MethodType.NORMAL
    assert str(model) == "MethodModel(test)"

    model.set_method_type(MethodType.STATIC)
    assert model.get_method_type() == MethodType.STATIC
    model.set_method_type(MethodType.ABSTRACT)
    assert model.get_method_type() == MethodType.ABSTRACT


def test_module_model_default():
    """Testing basics of class ModuleModel."""
    model = ModuleModel("pyclass2graph/parser/parser.py")
    assert model.get_name() == "parser"
    assert model.get_model_type() == ModelType.MODULE
    assert model.get_origin() == Origin.PACKAGE
    assert str(model) == "ModuleModel(parser)"


def test_dependency_model():
    """Testing of DependencyModel class."""
    classModel1 = ClassModel("source")
    classModel2 = ClassModel("destination")
    dependency = DependencyModel(classModel1, classModel2, DependencyType.BASE_CLASS)
    assert dependency.get_model_type() == ModelType.DEPENDENCY
    assert dependency.get_dependency_type() == DependencyType.BASE_CLASS
    assert dependency.get_origin() == Origin.PACKAGE
    assert dependency.get_source_model() == classModel1
    assert dependency.get_destination_model() == classModel2
    assert (
        str(dependency)
        == "DependencyModel(ClassModel(source), ClassModel(destination),DependencyType.BASE_CLASS)"
    )

    with pytest.raises(NotImplementedError):
        dependency.get_name()
