"""Module parser."""

from logging import getLogger, Logger

from .tools import ParserTools
from .model import (
    ClassModel,
    InstanceAttributeModel,
    DependencyModel,
    DependencyType,
    MethodModel,
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
        # provide final results
        return self.__moduleModels

    def parse_methods(self) -> None:
        """Parse methods and register it to the relating class."""
        for parsedClass in self.__parsedClasses:
            for node in ParserTools.find_all_methods(parsedClass["node"]):
                methodModel = MethodModel(node.name)

                classModel = parsedClass["model"]
                classModel.add_method(methodModel)

                methodModel.set_return_type(ParserTools.find_method_return_type(node))

                for (
                    argument_name,
                    argument_type,
                    names,
                ) in ParserTools.find_all_method_arguments(node):
                    methodArgumentModel = MethodArgumentModel(
                        argument_name, argument_type
                    )
                    methodModel.add_argument(methodArgumentModel)

                    for name in names:
                        destinationClassModel = self.__find_class_model_by_name(name)
                        if destinationClassModel:
                            methodModel.add_dependency(
                                DependencyModel(
                                    methodModel,
                                    destinationClassModel,
                                    DependencyType.METHOD_ARGUMENT,
                                )
                            )

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

                        for name in names:
                            destinationClassModel = self.__find_class_model_by_name(
                                name
                            )
                            if destinationClassModel:
                                instanceAttributeModel.add_dependency(
                                    DependencyModel(
                                        instanceAttributeModel,
                                        destinationClassModel,
                                        DependencyType.INSTANCE_ATTRIBUTE,
                                    )
                                )

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
                            sourceModel, destinationModel, DependencyType.BASE
                        )
                    )

    def __find_class_model_by_name(self, name: str) -> ClassModel | None:
        """Find a class model by name."""
        for parsedClass in self.__parsedClasses:
            classModel = parsedClass["model"]
            if classModel.get_name() == name:
                return classModel
        return None
