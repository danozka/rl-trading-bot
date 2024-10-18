import pkgutil

import fixtures


pytest_plugins: list[str] = [
    *(f'{fixtures.__name__}.{module}' for _, module, _ in pkgutil.iter_modules(fixtures.__path__))
]
