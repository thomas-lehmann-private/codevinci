# Quick Start

**Please note**: It will be available on PyPI when all features for first release are complete.

## Example usage with nox and Github

### Does require git

```python title="session in noxfile.py" linenums="1"
@nox.session
def codevinci_help(session: nox.Session) -> None:
    session.install('git+https://github.com/thomas-lehmann-private/codevinci.git@main')
    session.run('codevinci', '--help')
```

### Does not require git

```python title="session in noxfile.py" linenums="1"
@nox.session
def codevinci_help(session: nox.Session) -> None:
    session.install('https://github.com/thomas-lehmann-private/codevinci/archive/refs/heads/main.zip')
    session.run('codevinci', '--help')
```
