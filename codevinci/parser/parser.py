"""Module parser."""

from logging import getLogger, Logger
from typing import Generator, Iterable

from .tools import ParserTools
from .model import (
    AbstractBaseModel,
    ClassAttributeModel,
    ClassModel,
    InstanceAttributeModel,
    DependencyModel,
    DependencyType,
    MethodModel,
    MethodType,
    MethodArgumentModel,
    ModuleModel,
    Origin,
)


class Parser:
    """Parser for whole package path."""

    def __init__(self) -> None:
        """Initialize parser."""
        self.__logger: Logger = getLogger(__name__)
        self.__moduleModels: list[ModuleModel] = []
        self.__parsedClasses: list[dict] = []

    def parse(self, path: str) -> list[ModuleModel]:
        """Parse whole package."""
        # first get all classes
        for file, node in ParserTools.find_all_classes(path):
            # ensure the module does exist
            moduleModel = ModuleModel(file)
            if moduleModel in self.__moduleModels:
                moduleModel = self.__moduleModels[
                    self.__moduleModels.index(moduleModel)
                ]
            else:
                self.__moduleModels.append(moduleModel)

            # generate the class and add it to the model
            classModel = ClassModel(node.name)
            self.__logger.info(f"adding class {classModel.get_name()}")
            moduleModel.add_class(classModel)
            self.__parsedClasses.append(
                {"name": node.name, "node": node, "model": classModel}
            )

        # now search all methods for all classes
        self.parse_methods()
        # now parse all base class dependencies
        self.parse_bases()
        # now parse all instance attributes of a class for all classes
        self.parse_instance_attributes()
        # now parse all class attributes
        self.parse_class_attributes()
        # provide final results
        return self.__moduleModels

    def parse_string(self, code: str) -> list[ModuleModel]:
        """Parse code (can be used to get diagram from text or one file)."""
        moduleModel = ModuleModel("from code")
        self.__moduleModels.append(moduleModel)

        # first get all classes
        for node in ParserTools.find_all_classes_from_string(code):
            # generate the class and add it to the model
            classModel = ClassModel(node.name)
            self.__logger.info(f"adding class {classModel.get_name()}")
            moduleModel.add_class(classModel)
            self.__parsedClasses.append(
                {"name": node.name, "node": node, "model": classModel}
            )

        # now search all methods for all classes
        self.parse_methods()
        # now parse all base class dependencies
        self.parse_bases()
        # now parse all instance attributes of a class for all classes
        self.parse_instance_attributes()
        # now parse all class attributes
        self.parse_class_attributes()
        # provide final results
        return self.__moduleModels

    def create_dependencies(
        self,
        names: Iterable[str],
        sourceModel: AbstractBaseModel,
        dependencyType: DependencyType,
    ) -> Generator[DependencyModel, None, None]:
        """Create dependencies when a class of given packages is involved."""
        for name in names:
            destinationClassModel = self.__find_class_model_by_name(name)
            if destinationClassModel:
                yield DependencyModel(
                    sourceModel, destinationClassModel, dependencyType
                )

    def parse_methods(self) -> None:
        """Parse methods and register it to the relating class."""
        for parsedClass in self.__parsedClasses:
            for node in ParserTools.find_all_methods(parsedClass["node"]):
                methodModel = MethodModel(node.name)

                classModel = parsedClass["model"]
                classModel.add_method(methodModel)

                return_type, names = ParserTools.find_method_return_type(node)
                methodModel.set_return_type(return_type)
                for dependency in self.create_dependencies(
                    names, classModel, DependencyType.RETURN_TYPE
                ):
                    methodModel.add_dependency(dependency)

                for (
                    argument_name,
                    argument_type,
                    names,
                ) in ParserTools.find_all_method_arguments(node):
                    methodArgumentModel = MethodArgumentModel(
                        argument_name, argument_type
                    )
                    methodModel.add_argument(methodArgumentModel)

                    for dependency in self.create_dependencies(
                        names, methodModel, DependencyType.METHOD_ARGUMENT_TYPE
                    ):
                        methodModel.add_dependency(dependency)

                if ParserTools.is_static_method(node):
                    methodModel.set_method_type(MethodType.STATIC)
                elif ParserTools.is_abstract_method(node):
                    methodModel.set_method_type(MethodType.ABSTRACT)

    def parse_instance_attributes(self) -> None:
        """Parse instance attributes and register it to the relating class."""
        for parsedClass in self.__parsedClasses:
            classModel = parsedClass["model"]
            classNode = parsedClass["node"]

            for node in ParserTools.find_all_methods(classNode):
                if node.name == "__init__":
                    for (
                        attribute_name,
                        attribute_type,
                        names,
                    ) in ParserTools.find_all_instance_attributes(node):
                        instanceAttributeModel = InstanceAttributeModel(
                            attribute_name, attribute_type
                        )
                        classModel.add_attribute(instanceAttributeModel)

                        for dependency in self.create_dependencies(
                            names,
                            instanceAttributeModel,
                            DependencyType.INSTANCE_ATTRIBUTE_TYPE,
                        ):
                            instanceAttributeModel.add_dependency(dependency)

    def parse_class_attributes(self) -> None:
        """Parse class attributes and register it to the relating class."""
        for parsedClass in self.__parsedClasses:
            classModel = parsedClass["model"]
            classNode = parsedClass["node"]

            if not classModel.is_enum():
                continue

            for name in ParserTools.find_all_class_attributes(classNode):
                classModel.add_class_attribute(ClassAttributeModel(name))

    def parse_bases(self) -> None:
        """Parse for base class and register it as dependency to the relating class."""
        for parsedClass in self.__parsedClasses:
            for base in ParserTools.find_all_bases(parsedClass["node"]):
                # also allow 'Enum' and 'ABC' as dependencies
                destinationModel = (
                    ClassModel(base, Origin.BUILTIN)
                    if base in ["Enum", "ABC"]
                    else self.__find_class_model_by_name(base)
                )

                if destinationModel:
                    sourceModel = parsedClass["model"]
                    sourceModel.add_base(
                        DependencyModel(
                            sourceModel, destinationModel, DependencyType.BASE_CLASS
                        )
                    )

    def __find_class_model_by_name(self, name: str) -> ClassModel | None:
        """Find a class model by name."""
        for parsedClass in self.__parsedClasses:
            classModel = parsedClass["model"]
            if classModel.get_name() == name:
                return classModel
        return None
