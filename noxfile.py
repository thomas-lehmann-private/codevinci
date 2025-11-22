"""Module noxfile."""

from pathlib import Path

import nox

FILES = "noxfile.py", "pycodevinci.py", "codevinci"
FILES_WITH_TESTS = "noxfile.py", "pycodevinci.py", "codevinci", "tests"

ENV = {"PYTHONPATH": str(Path.cwd())}


@nox.session
def requirements(session: nox.Session):
    """Generate requirements.txt file"""
    session.install("pip-tools")
    session.run("pip-compile", "pyproject.toml")


@nox.session
def audit(session: nox.Session):
    """Checking for vulnerabilities in libraries."""
    session.install("pip-audit")
    session.run("pip-audit", "-r", "requirements.txt")


@nox.session
def black(session: nox.Session):
    """Run black for source code formatting."""
    session.install("black")
    session.run("black", *FILES_WITH_TESTS, env=ENV)


@nox.session
def bandit(session: nox.Session):
    """Run bad for security analysis."""
    session.install("bandit")
    session.run("bandit", "-r", *FILES, env=ENV)


@nox.session
def ruff(session: nox.Session):
    """Run ruff static code analysis."""
    # read here: https://docs.astral.sh/ruff/
    session.install("ruff")
    session.run("ruff", "check", env=ENV)


@nox.session
def pyright(session: nox.Session):
    """Run pyright static code analysis."""
    # read here: https://microsoft.github.io/pyright/#/
    session.install("pyright", "nox")
    session.install('-r', 'requirements.txt')
    session.run("pyright", env=ENV)


@nox.session
def radon(session: nox.Session):
    """Running complexity analysis."""
    session.install("radon")
    session.run("radon", "cc", "--min=B", "--total-average", *FILES, env=ENV)
    session.run("radon", "mi", "-s", *FILES_WITH_TESTS, env=ENV)


@nox.session
def interrogate(session: nox.Session):
    """Verify the source code documentation."""
    # read here: https://github.com/econchick/interrogate
    session.install("interrogate[png]")
    session.run("interrogate", "-v", "--fail-under=100", *FILES_WITH_TESTS, env=ENV)


@nox.session(python=["3.12", "3.13"], default=False)
def generate_classes_view(session):
    """Generate the class view of the package itself."""
    session.install('-r', 'requirements.txt')
    session.run(
        "python",
        "pycodevinci.py",
        "--package-path",
        "codevinci",
        "--output-format",
        "SVG",
        env=ENV,
    )


@nox.session
def pdoc(session: nox.Session):
    """Generating HTML documentation."""
    # read here: https://pdoc3.github.io/pdoc/
    session.install("pdoc")
    session.install('-r', 'requirements.txt')
    session.run("pdoc", "codevinci", "-o", "build/docs/html", env=ENV)


@nox.session
def mkdocs(session: nox.Session):
    """Running mkdocs for generating HTML documentation based on markdown."""
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


@nox.session
def pytest(session: nox.Session):
    """Running unittests."""
    session.install("pytest", "pytest-cov", "pytest-randomly", "pytest-codspeed")
    session.install('-r', 'requirements.txt')
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


@nox.session
def codspeed(session: nox.Session):
    """Running codspeed."""
    session.install("pytest", "pytest-codspeed")
    session.install('-r', 'requirements.txt')
    # separate run for code speed
    session.run("pytest", "tests", "--codspeed", env=ENV)


@nox.session
def build(session: nox.Session):
    """Build package."""
    session.install("build")
    session.run("python", "-m", "build", "--wheel", "--sdist", ".", env=ENV)


@nox.session(python=False, default=False)
def clean(session: nox.Session) -> None:
    """Cleanup temporary files and folders.

    Args:
        session (nox.Session): nox session.
    """
    session.run("git", "clean", "-fdX")


@nox.session(default=False)
def logo(session: nox.Session) -> None:
    session.install('svgwrite', 'cairosvg')
    session.run('python', 'scripts/logo.py')
