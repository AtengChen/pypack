import ast
import sys


MAP = {
    # "3.1": '("print" not in __import__("keyword").kwlist) and not ("argparse" in map(lambda x: x[1], __import__("pkgutil").iter_modules()))',
    # "3.2": '("argparse" in map(lambda x: x[1], __import__("pkgutil").iter_modules())) and not ("venv" in map(lambda x: x[1], __import__("pkgutil").iter_modules()))',
    # "3.3": '("venv" in map(lambda x: x[1], __import__("pkgutil").iter_modules())) and not ("asyncio" in map(lambda x: x[1], __import__("pkgutil").iter_modules()))',
    # "3.4": '("pathlib" in map(lambda x: x[1], __import__("pkgutil").iter_modules())) and not ("await" in __import__("keyword").kwlist)',
    # "3.5": '("async" in __import__("keyword").kwlist) and not (hasattr(__import__("math"), "tau"))',
    # "3.6": '("secrets" in map(lambda x: x[1], __import__("pkgutil").iter_modules())) and not ("breakpoint" in __builtins__.__dict__)',
    # "3.7": '("dataclasses" in map(lambda x: x[1], __import__("pkgutil").iter_modules())) and not hasattr(__import__("functools"), "cached_property")',
    "3.8": 'hasattr(__import__("ast"), "NamedExpr") and not hasattr(str, "removeprefix")',
    "3.9": 'hasattr(dict, "__ior__") and not ("zoneinfo" in map(lambda x: x[1], __import__("pkgutil").iter_modules()))',
    "3.10": 'hasattr(__import__("statistics"), "fmean") and not ("tomllib" in map(lambda x: x[1], __import__("pkgutil").iter_modules()))'
}


_ = sys.version_info
CURRENT_VERSION = f"{_.major}.{_.minor}"
del _


def get_determine_version(code: ast.AST, version: str = CURRENT_VERSION) -> ast.Expr:
    if version not in MAP:
        raise ValueError(f"Unsupported version {version}. Version must be in 3.8 to 3.10.")
    
    determine = f"({ast.unparse(code)}) if {MAP[version]} else __builtins__.__getattribute__('exit').__call__()"
    return ast.parse(determine).body[0]

