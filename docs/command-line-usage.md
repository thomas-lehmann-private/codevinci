# Command Line Usage

## Get main help

```
codevinci --help
Usage: codevinci [OPTIONS] COMMAND [ARGS]...

  CodeVinci is a Python source code analysis tool designed to generate clear,
  expressive diagrams of your project’s internal structure. By parsing Python
  modules, it extracts and visualizes:

  - Module relationships

  - Class hierarchies

  - Instance attributes

  - Methods and their arguments

  - Inter-module and inter-class dependencies

  The goal is to provide a powerful, modern alternative to tools like pdoc and
  pyreverse, with rich visual output, color-coded information layers, and an
  emphasis on intuitive understanding of complex codebases.

  In the future, CodeVinci will also support HTML documentation generation,
  using the same analysis engine to produce cohesive, navigable documentation
  for entire Python projects.

Options:
  --version  print version of this tool (and library)
  --help     Show this message and exit.

Commands:
  design  Generate diagram from Python code.
```

## Get design command group help

The final name of file cannot be changed and is one of **design.svg**,
**design.png** or **design.source**. The available names for overriding
the defaul colors are **title_color**, **attributes_color**,
**class_attributes_color**, **public_methods_color**, **protected_methods_color** and **private_methods_color**.

```
codevinci design --help
Usage: codevinci design [OPTIONS]

  Generate diagram from Python code.

Options:
  --package-path TEXT             root path to the packages
  --output-format [SVG|PNG|SOURCE]
                                  defines output format (default: SVG)
  --output-path TEXT              where to write the classes diagramm to
                                  (default: current path)
  --color TEXT                    Override colors, e.g. --color <name>:#ffeeaa
                                  (read doc)
  --aggregated-dependencies       reduce dependencies to class to class
  --help                          Show this message and exit.
```