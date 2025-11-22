# The build system

## Using nox

Everything starts with a build tool. I'm using **nox** (see [https://nox.thea.codes/en/stable/](https://nox.thea.codes/en/stable/)). The tool allows writing individual processes each of them focusing on a specific task (session). The header of the **noxfile.py** look similar to following:

```python
"""Module noxfile."""

import tomllib
from pathlib import Path

import nox

FILES = "noxfile.py", "pycodevinci.py", "codevinci"
FILES_WITH_TESTS = "noxfile.py", "pycodevinci.py", "codevinci", "tests"

ENV = {"PYTHONPATH": str(Path.cwd())}
```

The two constants **FILES** and **FILES_WITH_TESTS** are for different usecases and the ENV is that the package is found. The tasks in the **noxfile.py** are executed in given order of appearance in that file.

You simple execute it by calling `nox` or choosing a specific session like `nox -s black`.

## The session 'audit'

It does check vulnerabilities in given requirements.txt.

```python
@nox.session
def audit(session: nox.Session):
    """Checking for vulnerabilities in libraries."""
    session.install("pip-audit")
    session.run("pip-audit", "-r", "requirements.txt")
```

## The session 'black'

The tool is a source code formatter. See [https://black.readthedocs.io/en/stable/](https://black.readthedocs.io/en/stable/). The big advantage is that you don't have to care about. Please note that I also format the tests and even the **noxfile.py**.

```
@nox.session
def black(session: nox.Session):
    """Run black for source code formatting."""
    session.install("black")
    session.run("black", *FILES_WITH_TESTS, env=ENV)
```

## The session 'bandit'

This tool is to find security issues in your code. See [https://bandit.readthedocs.io/en/latest/](https://bandit.readthedocs.io/en/latest/).

```python
@nox.session
def bandit(session: nox.Session):
    """Run bandit for security analysis."""
    session.install("bandit")
    session.run("bandit", "-r", *FILES, env=ENV)
```

## The session 'ruff'

The tool is for static code analysis. See [https://docs.astral.sh/ruff/](https://docs.astral.sh/ruff/). It's very fast and does have a lot of rules.

```python
@nox.session
def ruff(session: nox.Session):
    """Run ruff static code analysis."""
    # read here: https://docs.astral.sh/ruff/
    session.install("ruff")
    session.run("ruff", "check", env=ENV)
```

## The session 'pyright'

This is also a static code analysis. See [https://microsoft.github.io/pyright/#/](https://microsoft.github.io/pyright/#/). Especially to mention is that this tool is capable to detect mismatch of defined types (by annotation) and usage.

```python
@nox.session
def pyright(session: nox.Session):
    """Run pyright static code analysis."""
    session.install("pyright", "nox")
    install_dependencies(session)
    session.run("pyright", env=ENV)
```

## The session 'radon'

The tool measures maintainability and complexity. See [https://radon.readthedocs.io/en/latest/](https://radon.readthedocs.io/en/latest/). The letters A to C indicates maintainability (**mi command**) were A means highly maintainable. The letters A to F for the **cc command** is about cyclomatic complexity where A does mean low complexity. So an 'A' is always appreciated.

```python
@nox.session
def radon(session: nox.Session):
    """Running complexity analysis."""
    session.install("radon")
    session.run("radon", "cc", "--min=B", "--total-average", *FILES, env=ENV)
    session.run("radon", "mi", "-s", *FILES_WITH_TESTS, env=ENV)
```

## The session 'interrogate'

The tool checks source code documentation. See [https://github.com/econchick/interrogate](https://github.com/econchick/interrogate). It is just about commenting each element. It does not check whether you document each parameter, return and exception (unfortunately).

```python
@nox.session
def interrogate(session: nox.Session):
    """Verify the source code documentation."""
    session.install("interrogate[png]")
    session.run("interrogate", "-v", "--fail-under=100", *FILES_WITH_TESTS, env=ENV)
```

## The session 'pdoc'

The tool does generate HTML as source code documentation. See [https://pdoc3.github.io/pdoc/](https://pdoc3.github.io/pdoc/). I miss some features focusing on this by the **codevinci** project. There is an alternative **sphinx** but the result is not convincing too.

```python
@nox.session
def pdoc(session: nox.Session):
    """Generating HTML documentation."""
    session.install("pdoc")
    install_dependencies(session)
    session.run("pdoc", "codevinci", "-o", "build/docs/html", env=ENV)
```

## The session 'mkdocs'

This tools generates this HTML and is great. See [https://www.mkdocs.org](https://www.mkdocs.org).

```python
@nox.session
def mkdocs(session: nox.Session):
    session.install(
        'mkdocs',
        'mkdocstrings',
        'mkdocs-material',
        'mkdocs-jupyter',
        'mkdocs-autolinks-plugin',
        'jupyter'
    )
    session.run(
        'mkdocs',
        'build',
        '--site-dir',
        'build/mkdocs',
        env=ENV)
```

## The session 'pytest'

It does run all tests including the docstring tests.
It also includes code coverage.
The tests are running in random order to ensure that tests are
really running isolated. See [https://docs.pytest.org/en/stable/](https://docs.pytest.org/en/stable/).

```python
@nox.session
def pytest(session: nox.Session):
    """Running unittests."""
    session.install("pytest", "pytest-cov", "pytest-randomly", "pytest-codspeed")
    install_dependencies(session)
    session.run(
        "pytest",
        "codevinci",
        "tests",
        "-v",
        "--doctest-modules",
        "--cov=codevinci",
        "--cov-fail-under=95",
        "--cov-report=xml",
        "--cov-report=html",
        "--cov-branch",
        "--junit-xml=unitTests.xml",
        env=ENV,
    )
```

## The session 'codspeed'

It is to run some benchmarks. See [https://github.com/CodSpeedHQ/pytest-codspeed](https://github.com/CodSpeedHQ/pytest-codspeed).

```python
@nox.session
def codspeed(session: nox.Session):
    """Running codspeed."""
    session.install("pytest", "pytest-codspeed")
    install_dependencies(session)
    # separate run for code speed
    session.run("pytest", "tests", "--codspeed", env=ENV)
```

## The session 'build'

It is the base to later on support the upload to PyPI. See [https://build.pypa.io/en/stable/](https://build.pypa.io/en/stable/).

```python
@nox.session
def build(session: nox.Session):
    """Build package."""
    session.install("build")
    session.run("python", "-m", "build", "--wheel", "--sdist", ".", env=ENV)
```

## The session 'clean'

Using git to remove the temporary files as mentioned in .gitignore

```python
@nox.session(python=False, default=False)
def clean(session: nox.Session) -> None:
    """Cleanup temporary files and folders.

    Args:
        session (nox.Session): nox session.
    """
    session.run("git", "clean", "-fdX")
```
