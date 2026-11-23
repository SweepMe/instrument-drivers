# ruff: noqa: INP001  # a script in tools/, not a package
"""Check SweepMe! drivers against the driver API and the style guidelines - a work list, not a test.

    python tools/check_driver.py src/SMU-Undalogic_miniSMU-MS01
    python tools/check_driver.py src --json > findings.json

The check reads the source only: it imports no driver (many need vendor libraries), changes nothing and always exits
with 0. Its findings are meant for an agent that works through them and runs the check again; a driver stays valid
without any of them. `warning` marks what is most likely wrong, `hint` what is worth a look.

What it checks follows the driver API (pysweepme @command, Literal, Annotated with Unit, Label and Range) and the
driver guide of this repository (DRIVER_GUIDE.md, sections 7 and 10):

    DC000  a file that cannot be parsed, or a folder named on the command line that holds no driver
    DC001  a command parameter without a type annotation
    DC002  a command without a return annotation
    DC003  a parameter compared with fixed strings: a Literal would list them
    DC004  a converted driver: a public method that looks like a command but is not decorated
    DC005  a setter that returns a value (setters and run commands return nothing; errors raise)
    DC006  a decorated reader without returns=(...)
    DC007  a command that calls other commands without composite=True
    DC008  a composite command that sends instrument commands itself, without a comment saying why
    DC009  (retired: a composite inherits the warnings of the commands it calls)
    DC010  two setters whose value parameters have the same name (one quantity in two meanings)
    DC011  @command is not the outermost decorator
    DC012  a check of what the annotation already says (@command checks choices and ranges)
    DC013  a "Warnings:" section written into a docstring instead of @command(warnings=...)
    DC014  a semantic function sends an instrument command a communication command also sends
    DC015  the semantic functions are not in the agreed order (the pairs, then the per-point functions)
    DC016  Unit, Label or Selector in a signature, or a Literal two commands write out, instead of a module alias
    DC017  a `description` class attribute (legacy; the documentation goes into doc/description.md)
    DC018  a command without a docstring
    DC019  a pair of semantic functions (connect/disconnect, ...) split by another method
    DC020  a setter's value parameter named generically (value, state, mode, ...) instead of after its quantity

What a modernization pass removes (DRIVER_GUIDE.md sections 4, 8, 10.1, 11.1 and 14):

    DC021  the legacy GUI API set_GUIparameter / get_GUIparameter instead of update_ / apply_gui_parameters
    DC022  parameters["Key"] indexed in a GUI method instead of parameters.get("Key", default)
    DC023  a deprecated call: find_Ports, stop_Measurement, stop_measurement, self.stopMeasurement, message_Box,
           write_Log, message_Info, get_Folder, is_run_aborted
    DC024  a bare `from EmptyDeviceClass import`, `from ErrorMessage import` or FolderManager import (use pysweepme)
    DC025  the folder key "SETTINGS" or "ROAMINGSETTINGS" in a folder lookup (now "SEQUENCES", "ROAMINGSEQUENCES")
    DC026  license.txt missing, or its copyright lines differ from those of the main.py header
    DC027  the latest copyright year is below the current year
    DC028  a .py file starting with a UTF-8 byte order mark

Only the .py files directly in a driver folder are read (main.py and the helper modules beside it, not libraries),
and license.txt beside main.py.

A finding that is deliberate is accepted with a comment saying why. For a finding about a method (also DC021 to
DC025 inside one) it stands on a decorator or the def line, or in the comment block directly above them - not inside
the body; for a finding about the file (DC015, DC017, DC019, DC026 to DC028, and DC021 to DC025 outside a method) on
the finding's line or the line above:

    # check_driver: ignore DC004 - a helper of the semantic functions, not a command
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import re
import sys
import warnings
from dataclasses import asdict, dataclass, field
from pathlib import Path

#: The semantic functions SweepMe!'s sequencer calls, in the order they stand in a driver (Axel, 2026-10-24): the
#: pairs, each opener directly followed by its closer, then the per-point functions in sequencer order. reconfigure
#: stands beside configure. They are not commands.
SEMANTIC_ORDER = (
    "connect", "disconnect", "initialize", "deinitialize", "configure", "unconfigure", "reconfigure",
    "poweron", "poweroff", "signin", "signout",
    "start", "apply", "reach", "adapt", "adapt_ready", "trigger_ready", "measure", "request_result", "read_result",
    "process_data", "call", "finish",
)
#: Semantic functions that belong together and stand next to each other.
PAIRS = (("connect", "disconnect"), ("initialize", "deinitialize"), ("configure", "unconfigure"),
         ("poweron", "poweroff"), ("signin", "signout"))
#: Methods of the driver framework (EmptyDevice and the GUI API) that are not commands either.
FRAMEWORK = (
    "set_GUIparameter", "get_GUIparameter", "update_gui_parameters", "apply_gui_parameters", "find_ports",
    "set_parameters", "get_parameters", "update_gui_parameters_with_fallback", "convert_gui_parameters",
    "message_box", "message_info", "message_log", "is_run_stopped", "get_folder", "get_variables", "get_units",
    "apply_selectors", "forget_selections", "selection_scope",
)
#: A public method whose name starts like this looks like a command.
COMMAND_PREFIXES = ("get_", "set_", "read_", "write_", "measure_", "fetch_", "enable_", "disable_", "start_", "stop_",
                    "reset", "trigger", "abort", "clear_", "is_")
CHANNEL_PARAMETERS = ("channel",)
#: Value parameter names that say nothing about the quantity a setter sets (DC020): renamed when a driver is touched.
GENERIC_VALUE_NAMES = ("value", "val", "state", "mode", "setting", "x", "v")
#: Markers that belong into a module-level alias (the quantity's unit and label, a selector), not into a signature
#: (DC016); a Range stays on the setter's parameter.
ALIAS_MARKERS = ("Unit", "Label", "Selector")
#: A comment accepting a finding where it is deliberate: "# check_driver: ignore DC004, DC010 - why".
IGNORE = re.compile(r"#\s*check_driver:\s*ignore\s+((?:DC\d{3}[,\s]*)+)", re.IGNORECASE)
PORT_METHODS = ("write", "query", "read", "write_raw", "read_raw")
#: The legacy GUI API (DC021) and the methods that receive the GUI parameters (DC022).
LEGACY_GUI = ("set_GUIparameter", "get_GUIparameter")
GUI_READERS = ("get_GUIparameter", "update_gui_parameters", "apply_gui_parameters")
#: Deprecated EmptyDevice names (DC023), called, assigned or overridden, and what replaces them.
DEPRECATED = {
    "find_Ports": "use find_ports (find_Ports is no longer called since SweepMe! 1.5.8)",
    "stop_Measurement": "raise an exception with a message for the user (section 8.1)",
    "stop_measurement": "raise an exception with a message for the user (section 8.1)",
    "stopMeasurement": "raise an exception with a message for the user (section 8.1)",
    "message_Box": "use message_box",
    "write_Log": "use message_log",
    "message_Info": "use message_info",
    "get_Folder": "use get_folder",
    "is_run_aborted": "use is_run_stopped",
}
#: Modules imported bare from SweepMe!'s path instead of from pysweepme (DC024), and what replaces them.
LEGACY_MODULES = {
    "EmptyDeviceClass": "from pysweepme import EmptyDevice",
    "ErrorMessage": "from pysweepme import debug, error",
    "FolderManager": "self.get_folder(key); libraries/ is on the path without addFolderToPATH",
}
#: Folder keys that no longer exist (DC025), and the calls that look a folder up by its key: EmptyDevice.get_folder
#: (get_Folder before), FolderManager.get_path.
OLD_FOLDER_KEYS = {"SETTINGS": "SEQUENCES", "ROAMINGSETTINGS": "ROAMINGSEQUENCES"}
FOLDER_LOOKUPS = ("get_folder", "get_Folder", "get_path")
COPYRIGHT = re.compile(r"^\s*#?\s*(copyright\b.*?)\s*$", re.IGNORECASE)
YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
BOM = b"\xef\xbb\xbf"
#: What is most likely wrong; every other code is a hint.
WARNINGS = {"DC000", "DC001", "DC002", "DC005", "DC006", "DC007", "DC011", "DC022"}


@dataclass
class Finding:
    """One thing worth a look, where it is and why."""

    code: str
    level: str  # "warning" or "hint"
    file: str
    line: int
    method: str
    message: str


@dataclass
class Method:
    """A function defined in a driver class, as the check sees it."""

    name: str
    node: ast.FunctionDef
    file: str
    path: Path
    cls: str = ""  # the class that defines it
    inherits: set[str] = field(default_factory=set)  # that class and its bases within the driver
    decorated: bool = False
    composite: bool = False
    has_returns: bool = False
    returned: tuple[str, ...] = ()  # the quantity names in returns=(...)
    warnings: bool = False
    kind_run: bool = False
    calls: set[str] = field(default_factory=set)  # self.<name>(...) calls
    port_heads: list[tuple[int, str]] = field(default_factory=list)  # instrument commands it sends

    @property
    def returns_none(self) -> bool:
        """Whether it is annotated -> None."""
        returns = self.node.returns
        return isinstance(returns, ast.Constant) and returns.value is None

    @property
    def parameters(self) -> list[ast.arg]:
        """The parameters a caller passes (self left out)."""
        args = self.node.args
        return [a for a in [*args.posonlyargs, *args.args, *args.kwonlyargs] if a.arg != "self"]


@dataclass
class Driver:
    """A driver folder: its methods across the .py files beside main.py, and the module-level aliases."""

    folder: Path
    methods: dict[str, Method] = field(default_factory=dict)  # keyed "file:Class.name", so classes stay apart
    bases: dict[str, list[str]] = field(default_factory=dict)  # class name -> names of its base classes
    order: list[tuple[str, str, str, int]] = field(default_factory=list)  # (file, class, name, line) as defined
    checked_aliases: set[str] = field(default_factory=set)  # aliases with a Literal or a Range inside
    selector_aliases: set[str] = field(default_factory=set)  # aliases with a Selector(...) inside
    description_attributes: list[tuple[str, int]] = field(default_factory=list)
    unreadable: list[tuple[str, int, str]] = field(default_factory=list)
    paths: dict[str, Path] = field(default_factory=dict)  # every .py file read, by its reported name
    trees: dict[str, ast.Module] = field(default_factory=dict)  # the syntax trees of the files that parse

    @property
    def declared(self) -> bool:
        """Whether the driver uses @command (then only decorated methods are commands)."""
        return any(m.decorated for m in self.methods.values())


@dataclass
class Report:
    """The findings of one driver."""

    findings: list[Finding] = field(default_factory=list)
    owners: list[Method | None] = field(default_factory=list)  # the method of each finding, for the ignore comments

    def add(self, code: str, method: Method | None, line: int, message: str, file: str = "") -> None:
        """Note one finding; its level follows from the code."""
        level = "warning" if code in WARNINGS else "hint"
        self.findings.append(Finding(code, level, file or (method.file if method else ""), line,
                                     method.name if method else "", message))
        self.owners.append(method)


# --- reading a driver --------------------------------------------------------------------------------------------

def _decorator_name(node: ast.expr) -> str:
    """The name of a decorator: 'command' for @command and @command(...)."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Attribute):
        return target.attr
    return target.id if isinstance(target, ast.Name) else ""


def _keyword(decorator: ast.expr, name: str) -> ast.expr | None:
    """The value of a keyword argument of a decorator call."""
    if isinstance(decorator, ast.Call):
        for keyword in decorator.keywords:
            if keyword.arg == name:
                return keyword.value
    return None


def _command_head(node: ast.expr) -> str:
    """An instrument command as text up to its first space, placeholders as {}: 'SOUR{}:VOLT'."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        text = node.value
    elif isinstance(node, ast.JoinedStr):
        text = "".join(part.value if isinstance(part, ast.Constant) else "{}" for part in node.values)
    elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "format"
          and isinstance(node.func.value, ast.Constant) and isinstance(node.func.value.value, str)):
        text = re.sub(r"\{[^}]*\}", "{}", node.func.value.value)
    else:
        return ""
    return text.strip().split(" ")[0].upper()  # the query marker stays: 'VOLT?' is not 'VOLT'


def _uses_names(node: ast.AST) -> set[str]:
    """Every plain name used in an expression."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _method(node: ast.FunctionDef, file: str, path: Path, cls: str) -> Method:
    """A method with what its decorators and its body say."""
    method = Method(node.name, node, file, path, cls)
    for decorator in node.decorator_list:
        if _decorator_name(decorator) == "command":
            method.decorated = True
            composite = _keyword(decorator, "composite")
            method.composite = isinstance(composite, ast.Constant) and composite.value is True
            returns = _keyword(decorator, "returns")
            method.has_returns = returns is not None
            if isinstance(returns, (ast.Tuple, ast.List)):
                method.returned = tuple(e.value for e in returns.elts
                                        if isinstance(e, ast.Constant) and isinstance(e.value, str))
            method.warnings = _keyword(decorator, "warnings") is not None
            kind = _keyword(decorator, "kind")
            method.kind_run = isinstance(kind, ast.Constant) and kind.value == "run"
    own_scope = _own_scope(node)  # a call inside a nested function is not a call the method makes
    for sub in ast.walk(node):
        if not (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)):
            continue
        owner = sub.func.value
        if isinstance(owner, ast.Name) and owner.id == "self":
            if sub in own_scope:
                method.calls.add(sub.func.attr)
        elif (sub.func.attr in PORT_METHODS and isinstance(owner, ast.Attribute) and owner.attr == "port"
              and isinstance(owner.value, ast.Name) and owner.value.id == "self"):
            method.port_heads.append((sub.lineno, _command_head(sub.args[0]) if sub.args else ""))
    return method


def _parse(path: Path) -> ast.Module:
    """A file's syntax tree; a byte order mark and old drivers' invalid escapes are not findings."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        return ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))


def _read_module(tree: ast.Module, file: str, path: Path, driver: Driver) -> None:
    """The aliases, classes and methods of one file of a driver."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            value = ast.unparse(node.value)
            if value.startswith(("Literal[", "Annotated[")) and ("Literal[" in value or "Range(" in value):
                driver.checked_aliases.add(node.targets[0].id)
            if value.startswith("Annotated[") and "Selector(" in value:
                driver.selector_aliases.add(node.targets[0].id)
        if not isinstance(node, ast.ClassDef):
            continue
        driver.bases[node.name] = [ast.unparse(base).split(".")[-1] for base in node.bases]
        for item in node.body:
            if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "description"
                                                    for t in item.targets):
                driver.description_attributes.append((file, item.lineno))
            if isinstance(item, ast.FunctionDef):
                driver.methods[f"{file}:{node.name}.{item.name}"] = _method(item, file, path, node.name)
                driver.order.append((file, node.name, item.name, item.lineno))


def _class_chain(cls: str, driver: Driver) -> set[str]:
    """A class and the base classes the driver itself defines, whose methods it inherits."""
    chain, todo = set(), [cls]
    while todo:
        name = todo.pop()
        if name in chain or name not in driver.bases:
            continue
        chain.add(name)
        todo.extend(driver.bases[name])
    return chain


def _class_commands(method: Method, commands: list[Method]) -> set[str]:
    """The names a self.<name>(...) call in the method can reach: the commands of its class and its bases."""
    return {c.name for c in commands if c.cls in method.inherits}


def _file_name(path: Path, folder: Path) -> str:
    """How a finding names a file of the driver: from the folder above the driver folders, e.g. src/X/main.py."""
    return str(path.relative_to(folder.parent.parent)) if folder.parent.parent in path.parents else str(path)


def read_driver(folder: Path) -> Driver:
    """Collect the classes' methods and the module-level aliases of a driver folder."""
    driver = Driver(folder)
    trees = []
    for path in sorted(folder.glob("*.py")):
        file = _file_name(path, folder)
        driver.paths[file] = path
        try:
            tree = _parse(path)
        except (SyntaxError, UnicodeDecodeError, OSError) as exc:  # a file that cannot be read is DC000 too
            driver.unreadable.append((file, getattr(exc, "lineno", 0) or 0, str(exc)))
            continue
        trees.append(tree)
        driver.trees[file] = tree
        _read_module(tree, file, path, driver)
    # an alias built on an alias that has a choice, a range or a selector has it too
    for tree in trees:
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                if _uses_names(node.value) & driver.checked_aliases:
                    driver.checked_aliases.add(node.targets[0].id)
                if _uses_names(node.value) & driver.selector_aliases:
                    driver.selector_aliases.add(node.targets[0].id)
    for method in driver.methods.values():
        method.inherits = _class_chain(method.cls, driver)
    return driver


def _is_selector(parameter: ast.arg, driver: Driver) -> bool:
    """A parameter that addresses a part of the instrument: marked Selector() through an alias or inline, or channel.

    Its value says where a setter acts, not what it sets, so it is no quantity of DC010 and DC020.
    """
    annotation = parameter.annotation
    if annotation is not None and (_uses_names(annotation) & driver.selector_aliases
                                   or "Selector(" in ast.unparse(annotation)):
        return True
    return parameter.arg in CHANNEL_PARAMETERS


def _is_command_like(method: Method) -> bool:
    """A public method that is neither a semantic function nor framework API, named or acting like a command."""
    name = method.name
    if name.startswith("_") or name in SEMANTIC_ORDER or name in FRAMEWORK:
        return False
    return name.startswith(COMMAND_PREFIXES) or bool(method.port_heads)


# --- the checks --------------------------------------------------------------------------------------------------

def check_driver(folder: Path) -> list[Finding]:
    """Every finding for one driver folder, in file and line order."""
    driver = read_driver(folder)
    report = Report()
    for file, line, message in driver.unreadable:
        report.add("DC000", None, line, f"cannot be parsed: {message}", file)

    if driver.declared:
        commands = [m for m in driver.methods.values() if m.decorated]
    else:
        commands = [m for m in driver.methods.values() if _is_command_like(m)]
    for method in commands:
        _check_command(method, driver, _class_commands(method, commands), report)
    _shared_inline_literals(commands, report)

    if driver.declared:
        for method in driver.methods.values():
            if not method.decorated and _is_command_like(method):
                report.add("DC004", method, method.node.lineno,
                           "looks like a command but is not decorated - in a driver using @command it is not offered")
        _duplicate_quantities(commands, driver, report)
    _generic_value_names(commands, driver, report)
    _semantic_raw_commands(driver, commands, report)
    _semantic_order(driver, report)
    _split_pairs(driver, report)
    for file, line in driver.description_attributes:
        report.add("DC017", None, line,
                   "a `description` class attribute - write the documentation into doc/description.md", file)
    _legacy_api(driver, report)
    _license(driver, report)
    _byte_order_marks(driver, report)
    kept =(f for f, m in zip(report.findings, report.owners, strict=True) if not _ignored(f, m, driver))
    return sorted(kept, key=lambda f: (f.file, f.line, f.code))


def _first_line(node: ast.FunctionDef) -> int:
    """The line a method starts on: its first decorator, or the def line without decorators."""
    return min((decorator.lineno for decorator in node.decorator_list), default=node.lineno)


def _ignored(finding: Finding, method: Method | None, driver: Driver) -> bool:
    """Whether a comment accepts the finding.

    It stands on the method's decorators or def line or in the comment block right above them, or for a finding about
    the file on the finding's line or the line above.
    """
    path: Path | None
    if method is not None:
        first = _first_line(method.node) - 1  # the line above the first decorator (or the def)
        last = method.node.body[0].lineno - 1 if method.node.body else method.node.lineno
        path = method.path
    else:
        first, last = finding.line - 1, finding.line
        path = driver.paths.get(finding.file)
    if path is None:
        return False
    lines = _lines(path)
    if method is not None:
        while first > 1 and lines[first - 2].strip().startswith("#"):  # a reason may take several lines
            first -= 1
    for line in lines[max(first - 1, 0):last]:
        match = IGNORE.search(line)
        if match and finding.code in re.findall(r"DC\d{3}", match.group(1).upper()):
            return True
    return False


_LINES: dict[Path, list[str]] = {}


def _lines(path: Path) -> list[str]:
    """The lines of a file, read once."""
    if path not in _LINES:
        try:
            _LINES[path] = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()
        except OSError:
            _LINES[path] = []
    return _LINES[path]


def _check_command(method: Method, driver: Driver, command_names: set[str], report: Report) -> None:
    """The checks of one command: annotations, docstring, what it returns, composite, decorator order."""
    node = method.node
    for parameter in method.parameters:
        if parameter.annotation is None:
            report.add("DC001", method, node.lineno, f"parameter '{parameter.arg}' has no type annotation")
        elif markers := _inline_markers(parameter.annotation):
            report.add("DC016", method, node.lineno,
                       f"'{parameter.arg}' has {', '.join(markers)} inline - put it into an alias at module level; "
                       f"only a Range belongs on the parameter")
    if node.returns is None:
        report.add("DC002", method, node.lineno, "no return annotation (-> None for a setter or a run command)")
    docstring = ast.get_docstring(node)
    if not docstring:
        report.add("DC018", method, node.lineno, "no docstring")
    elif re.search(r"^\s*Warnings?:", docstring, re.MULTILINE) and not method.warnings:
        report.add("DC013", method, node.lineno,
                   "a Warnings section in the docstring - say it in @command(warnings=...), which adds the section")
    if method.decorated and node.returns is not None and not method.returns_none and not method.has_returns:
        report.add("DC006", method, node.lineno,
                   "a reader without returns=(...) - the driver does not load (pysweepme raises a TypeError)")
    if method.name.startswith("set_") or (method.decorated and (method.returns_none or method.kind_run)):
        _returned_value(method, report)
    if method.decorated and _decorator_name(node.decorator_list[0]) != "command":
        report.add("DC011", method, node.lineno,
                   "@command is not the outermost decorator - a decorator above it may drop the marker")
    _composite(method, command_names, report)
    _redundant_checks(method, driver, report)
    _literal_candidates(method, report)


def _own_scope(node: ast.AST) -> list[ast.AST]:
    """The nodes of a function body without those of nested functions, lambdas and classes."""
    found: list[ast.AST] = []
    todo: list[ast.AST] = list(ast.iter_child_nodes(node))
    while todo:
        sub = todo.pop()
        found.append(sub)
        if not isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            todo.extend(ast.iter_child_nodes(sub))
    return found


def _returned_value(method: Method, report: Report) -> None:
    """DC005: a setter or a run command that returns something (a return of a nested function is its own)."""
    for sub in _own_scope(method.node):
        if isinstance(sub, ast.Return) and sub.value is not None and not (
                isinstance(sub.value, ast.Constant) and sub.value.value is None):
            report.add("DC005", method, sub.lineno,
                       "returns a value - a setter or run command returns nothing and raises when something is wrong; "
                       "what it produced is read with a getter")
            return


def _composite(method: Method, command_names: set[str], report: Report) -> None:
    """DC007, DC008: a command that calls commands, and what a composite one does itself."""
    called = method.calls & command_names - {method.name}
    if method.decorated and called and not method.composite:
        report.add("DC007", method, method.node.lineno,
                   f"calls the commands {', '.join(sorted(called))} - declare it @command(composite=True)")
    if not method.composite:
        return
    if method.port_heads and not _commented(method):
        report.add("DC008", method, method.port_heads[0][0],
                   "a composite command that sends instrument commands itself - call the commands, or say in a "
                   "comment why not (e.g. fewer round trips)")


def _commented(method: Method) -> bool:
    """Whether the instrument commands a composite sends itself come with a reason.

    A comment on the line of a self.port call, or in the comment block directly above it, counts; a comment elsewhere
    in the method does not. An accepted finding (`# check_driver: ignore DC008 - why`) is handled by _ignored.
    """
    lines = _lines(method.path)
    for line_number, _ in method.port_heads:
        on_line = lines[line_number - 1] if line_number <= len(lines) else ""
        above = lines[line_number - 2] if line_number > 1 else ""
        if "#" in on_line or above.strip().startswith("#"):
            return True
    return False


def _redundant_checks(method: Method, driver: Driver, report: Report) -> None:
    """DC012: an if that raises on a parameter whose annotation already states the choices or the range."""
    if not method.decorated:
        return
    checked = {p.arg for p in method.parameters
               if p.annotation is not None and (_uses_names(p.annotation) & driver.checked_aliases
                                                or "Literal[" in ast.unparse(p.annotation)
                                                or "Range(" in ast.unparse(p.annotation))}
    for sub in ast.walk(method.node):
        if (checked and isinstance(sub, ast.If) and _uses_names(sub.test) & checked
                and any(isinstance(n, ast.Raise) for n in sub.body) and _static_check(sub.test, checked)):
            names = ", ".join(sorted(_uses_names(sub.test) & checked))
            report.add("DC012", method, sub.lineno,
                       f"checks {names} although its annotation states the choices or range - @command checks them")
            return


def _static_check(test: ast.expr, checked: set[str]) -> bool:
    """Whether a condition compares checked parameters with constants only.

    A bound known only at run time (`voltage > self.max_voltage`, a value read from the instrument) is nothing a Range
    or Literal states, so such a check stays.
    """
    if isinstance(test, ast.BoolOp):
        return all(_static_check(value, checked) for value in test.values)
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _static_check(test.operand, checked)
    if not isinstance(test, ast.Compare):
        return False
    operands = [test.left, *test.comparators]
    return any(isinstance(o, ast.Name) and o.id in checked for o in operands) and all(
        _is_constant(o) or (isinstance(o, ast.Name) and o.id in checked) for o in operands)


def _is_constant(node: ast.expr) -> bool:
    """A literal: a number or text, also negative, or a tuple, list or set of them."""
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return _is_constant(node.operand)
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(_is_constant(e) for e in node.elts)
    return False


def _literal_candidates(method: Method, report: Report) -> None:
    """DC003: a str or unannotated parameter compared with at least two fixed, non-empty strings."""
    plain = {p.arg for p in method.parameters
             if p.annotation is None or ast.unparse(p.annotation) in ("str", "'str'")}
    seen: dict[str, set[str]] = {}
    for sub in ast.walk(method.node):
        if not (plain and isinstance(sub, ast.Compare)):
            continue
        name = _compared_name(sub.left)
        if name not in plain:
            continue
        for op, comparator in zip(sub.ops, sub.comparators, strict=True):
            if isinstance(op, (ast.Eq, ast.NotEq, ast.In, ast.NotIn)):
                seen.setdefault(name, set()).update(s for s in _string_constants(comparator) if s.strip())
    for name, strings in seen.items():
        if len(strings) > 1:
            listed = ", ".join(repr(s) for s in sorted(strings))
            report.add("DC003", method, method.node.lineno,
                       f"'{name}' is compared with {listed} - a Literal alias would list the choices")


def _compared_name(node: ast.expr) -> str:
    """The parameter a comparison is about: `mode`, `mode.upper()` and `str(mode)` alike."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        return node.func.value.id
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "str"
            and node.args and isinstance(node.args[0], ast.Name)):
        return node.args[0].id
    return ""


def _string_constants(node: ast.expr) -> list[str]:
    """The strings a comparison is against: "A", or ("A", "B")."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values = [e.value for e in node.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        return values if len(values) == len(node.elts) else []
    return []


def _duplicate_quantities(commands: list[Method], driver: Driver, report: Report) -> None:
    """DC010: setters whose value parameters share a name, so two quantities would share one recorded series."""
    owners: dict[str, list[Method]] = {}
    for method in commands:
        if not method.returns_none or method.kind_run or method.composite:
            continue
        for parameter in method.parameters:
            if not _is_selector(parameter, driver):
                owners.setdefault(parameter.arg, []).append(method)
    for name, methods in sorted(owners.items()):
        if len({m.name for m in methods}) > 1:  # an override in a subclass is the same setter
            listed = ", ".join(dict.fromkeys(m.name for m in methods))
            report.add("DC010", methods[1], methods[1].node.lineno,
                       f"the value parameter '{name}' is set by {listed} - name each after what it sets, "
                       f"or they are one quantity in the recorded values")


def _inline_markers(annotation: ast.expr) -> list[str]:
    """DC016: the markers of an inline Annotated[...] that belong into an alias; a Range stays on the parameter."""
    if not (isinstance(annotation, ast.Subscript) and ast.unparse(annotation.value).endswith("Annotated")
            and isinstance(annotation.slice, ast.Tuple)):
        return []
    return [name for marker in annotation.slice.elts[1:]
            if isinstance(marker, ast.Call) and (name := ast.unparse(marker.func).split(".")[-1]) in ALIAS_MARKERS]


def _shared_inline_literals(commands: list[Method], report: Report) -> None:
    """DC016: the same Literal written out in the signatures of two or more commands, which then drift apart."""
    users: dict[str, list[Method]] = {}
    for method in commands:
        for parameter in method.parameters:
            if parameter.annotation is not None and ast.unparse(parameter.annotation).startswith("Literal["):
                users.setdefault(ast.unparse(parameter.annotation), []).append(method)
    for choices, methods in users.items():
        if len({m.name for m in methods}) > 1:
            for method in methods:
                report.add("DC016", method, method.node.lineno,
                           f"{choices} is written out in {len(methods)} commands - name the choices once as an alias "
                           f"at module level")


def _generic_value_names(commands: list[Method], driver: Driver, report: Report) -> None:
    """DC020: a setter's value parameter named `value`, `state`, `mode`, ... - the recorded series takes its name.

    A setter is a method annotated -> None, or in an undeclared driver one named set_...; the renaming break is
    accepted whenever a driver is touched (Driver API concept, review point 4). A name that a reader of the driver
    returns is the quantity's own name (move_to(x, y, z) beside get_position returning x, y, z).
    """
    returned = {name for method in commands for name in method.returned}
    for method in commands:
        if method.kind_run or method.composite:
            continue
        if not (method.returns_none or (not method.decorated and method.name.startswith("set_"))):
            continue
        for parameter in method.parameters:
            if (parameter.arg.lower() in GENERIC_VALUE_NAMES and parameter.arg not in returned
                    and not _is_selector(parameter, driver)):
                report.add("DC020", method, method.node.lineno,
                           f"the value parameter '{parameter.arg}' does not say what it sets - name it after its "
                           f"quantity (voltage, operation_mode, current_range), which names the recorded series")


def _semantic_raw_commands(driver: Driver, commands: list[Method], report: Report) -> None:
    """DC014: a semantic function sends an instrument command that a communication command also sends."""
    for method in driver.methods.values():
        if method.name not in SEMANTIC_ORDER:
            continue
        wrapped: dict[str, str] = {}  # the commands the semantic function can call: its class and its bases
        for command in commands:
            if command.cls in method.inherits:
                for _, head in command.port_heads:
                    if head:
                        wrapped.setdefault(head, command.name)
        for line, head in method.port_heads:
            if head in wrapped:
                report.add("DC014", method, line, f"sends '{head}' itself, which {wrapped[head]}() also sends - "
                                                    f"call it where it does the same")


def _semantic_order(driver: Driver, report: Report) -> None:
    """DC015: the semantic functions of a file in the agreed order (SEMANTIC_ORDER)."""
    by_file: dict[str, list[tuple[int, str]]] = {}
    for file, cls, name, line in driver.order:
        if name in SEMANTIC_ORDER:
            by_file.setdefault(f"{file}:{cls}", []).append((line, name))
    for key, defined in by_file.items():
        file = key.rsplit(":", 1)[0]
        names = [name for _, name in sorted(defined)]
        expected = sorted(names, key=SEMANTIC_ORDER.index)
        if names != expected:
            first = next(i for i, (a, b) in enumerate(zip(names, expected, strict=True)) if a != b)
            report.add("DC015", None, sorted(defined)[first][0],
                       f"semantic functions out of order: {', '.join(names)} - expected "
                       f"{', '.join(expected)}", file)


def _split_pairs(driver: Driver, report: Report) -> None:
    """DC019: an opener and its closer (connect/disconnect, ...) with another method defined between them."""
    for file, cls in {(file, cls) for file, cls, _, _ in driver.order}:
        defined = sorted(((line, name) for f, c, name, line in driver.order if (f, c) == (file, cls)))
        names = [name for _, name in defined]
        lines = {name: line for line, name in defined}
        for opener, closer in PAIRS:
            if opener in names and closer in names and names.index(closer) != names.index(opener) + 1:
                report.add("DC019", None, lines[closer],
                           f"{closer} does not directly follow {opener} - keep the pair together", file)


# --- what a modernization pass removes ---------------------------------------------------------------------------

def _owner(driver: Driver, file: str, line: int) -> Method | None:
    """The method a line of a file belongs to (its ignore comment accepts the finding), or None outside methods."""
    owners = [m for m in driver.methods.values()
              if m.file == file and _first_line(m.node) <= line <= (m.node.end_lineno or m.node.lineno)]
    return max(owners, key=lambda m: _first_line(m.node), default=None)


def _legacy_api(driver: Driver, report: Report) -> None:
    """DC021 to DC025: the legacy GUI API, indexed GUI parameters, deprecated calls, imports and folder keys."""
    for file, tree in driver.trees.items():
        for node in ast.walk(tree):
            if found := _legacy_finding(node):
                report.add(found[0], _owner(driver, file, node.lineno), node.lineno, found[1], file)
    for method in driver.methods.values():
        if method.name in GUI_READERS:
            _indexed_parameters(method, report)


def _legacy_finding(node: ast.AST) -> tuple[str, str] | None:
    """The code and message of DC021, DC023, DC024 or DC025 for one node of a syntax tree, or None."""
    if isinstance(node, ast.FunctionDef) and node.name in LEGACY_GUI:
        return "DC021", (f"the legacy GUI API {node.name} - use update_gui_parameters and apply_gui_parameters "
                         f"(DRIVER_GUIDE.md section 4), keeping every GUI key")
    if isinstance(node, ast.FunctionDef) and node.name in DEPRECATED:
        return "DC023", f"overrides the deprecated {node.name} - {DEPRECATED[node.name]}"
    if isinstance(node, ast.Attribute) and node.attr in DEPRECATED:
        return "DC023", f"the deprecated {node.attr} - {DEPRECATED[node.attr]}"
    if isinstance(node, (ast.Import, ast.ImportFrom)) and (module := _legacy_module(node)):
        return "DC024", f"imports {module} from SweepMe!'s path - use {LEGACY_MODULES[module]}"
    if isinstance(node, ast.Call) and (key := _old_folder_key(node)):
        return "DC025", f'the folder key "{key}" no longer exists - use "{OLD_FOLDER_KEYS[key]}"'
    return None


def _legacy_module(node: ast.Import | ast.ImportFrom) -> str:
    """The legacy module a bare import names: `from EmptyDeviceClass import ...`, `import FolderManager as FoMa`."""
    if isinstance(node, ast.ImportFrom):
        return node.module if node.level == 0 and node.module in LEGACY_MODULES else ""
    return next((alias.name for alias in node.names if alias.name in LEGACY_MODULES), "")


def _old_folder_key(node: ast.Call) -> str:
    """A folder key that no longer exists, passed to a folder lookup: get_folder("SETTINGS"), FoMa.get_path(...)."""
    if _call_name(node) not in FOLDER_LOOKUPS:
        return ""
    for argument in node.args:
        if isinstance(argument, ast.Constant) and argument.value in OLD_FOLDER_KEYS:
            return str(argument.value)
    return ""


def _call_name(node: ast.Call) -> str:
    """The name a call is made by: 'get_folder' for self.get_folder(...) and get_folder(...)."""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return node.func.id if isinstance(node.func, ast.Name) else ""


def _indexed_parameters(method: Method, report: Report) -> None:
    """DC022: parameters["Key"] in a method that receives the GUI parameters, which may come incomplete."""
    received = [p.arg for p in method.parameters]
    if not received:
        return
    name = received[0]
    indexed = [sub for sub in ast.walk(method.node) if isinstance(sub, ast.Subscript) and isinstance(sub.ctx, ast.Load)
               and isinstance(sub.value, ast.Name) and sub.value.id == name]
    if indexed:
        report.add("DC022", method, indexed[0].lineno,
                   f"{name}[...] indexed {len(indexed)} time(s) - read every key with {name}.get(key, default): "
                   f"the dict may come without the key (section 4.3)")


def _current_year() -> int:
    """The year the copyright ranges are extended to."""
    return dt.datetime.now(tz=dt.UTC).year


def _copyright_lines(lines: list[str], *, comments: bool) -> list[tuple[int, str]]:
    """The copyright lines of a file with their line numbers, whitespace collapsed; in code only comment lines."""
    found = []
    for number, line in enumerate(lines, 1):
        if comments and not line.lstrip().startswith("#"):
            continue
        match = COPYRIGHT.match(line)
        if match:
            found.append((number, " ".join(match.group(1).split())))
    return found


def _license(driver: Driver, report: Report) -> None:
    """DC026, DC027: license.txt beside main.py with the copyright lines of the header, the year range up to date."""
    main = driver.folder / "main.py"
    file = _file_name(main, driver.folder)
    header = _copyright_lines(_lines(main), comments=True)
    line = header[0][0] if header else 1
    license_file = next((p for p in driver.folder.iterdir() if p.name.lower() == "license.txt"), None)
    if license_file is None:
        report.add("DC026", None, line, "no license.txt beside main.py - add the license (MIT whenever possible) with "
                                        "the copyright line of the header (section 14)", file)
        licensed: list[tuple[int, str]] = []
    else:
        licensed = _copyright_lines(_lines(license_file), comments=False)
        ours, theirs = [text for _, text in header], [text for _, text in licensed]
        if not ours:
            report.add("DC026", None, line, "no copyright line in the header of main.py - add the one of license.txt",
                       file)
        elif ours != theirs:
            report.add("DC026", None, line, f"the copyright lines differ: main.py has {ours}, license.txt has "
                                            f"{theirs} - both carry the same lines", file)
    years = [int(year) for _, text in header + licensed for year in YEAR.findall(text)]
    current = _current_year()
    if years and max(years) < current:
        report.add("DC027", None, line, f"the latest copyright year is {max(years)} - extend the range to {current} "
                                        f"in main.py and license.txt (e.g. {min(years)}-{current})", file)


def _byte_order_marks(driver: Driver, report: Report) -> None:
    """DC028: a .py file that starts with a UTF-8 byte order mark."""
    for file, path in driver.paths.items():
        try:
            head = path.read_bytes()[:len(BOM)]
        except OSError:
            continue
        if head == BOM:
            report.add("DC028", None, 1, "starts with a UTF-8 byte order mark - save it as UTF-8 without BOM", file)


# --- command line ------------------------------------------------------------------------------------------------

def driver_folders(paths: list[str]) -> tuple[list[Path], list[Path]]:
    """The driver folders named, or every driver folder below a folder like src; and the folders holding none."""
    folders: list[Path] = []
    empty: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if (path / "main.py").is_file():
            folders.append(path)
        elif path.is_dir():
            below = sorted(p for p in path.iterdir() if (p / "main.py").is_file())
            folders.extend(below)
            if not below:
                empty.append(path)
        else:
            sys.stderr.write(f"not a driver folder: {path}\n")
    return folders, empty


def _report_names(folders: list[Path]) -> list[str]:
    """One name per folder: the folder's name, or its path where two folders share a name."""
    names = [folder.name for folder in folders]
    return [name if names.count(name) == 1 else str(folder) for name, folder in zip(names, folders, strict=True)]


def main(argv: list[str] | None = None) -> int:
    """Check the drivers named on the command line and write the findings to stdout."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("paths", nargs="+", help="driver folders, or a folder holding driver folders (e.g. src)")
    parser.add_argument("--json", action="store_true", help="write the findings as JSON, for an agent")
    parser.add_argument("--only", default="", help="comma-separated codes to report, e.g. DC005,DC010")
    parser.add_argument("--warnings", action="store_true", help="report warnings only, no hints")
    args = parser.parse_args(argv)

    only = {code.strip().upper() for code in args.only.split(",") if code.strip()}
    folders, empty = driver_folders(args.paths)
    report = {name: [f for f in check_driver(folder)
                     if (not only or f.code in only) and (not args.warnings or f.level == "warning")]
              for name, folder in zip(_report_names(folders), folders, strict=True)}
    for path in empty:  # a folder that exists but holds no driver is reported, not silently left out
        finding = Finding("DC000", "warning", str(path), 0, "",
                          "no driver here: neither this folder nor a folder directly below it has a main.py")
        report[str(path)] = [finding] if (not only or "DC000" in only) else []

    if args.json:
        json.dump({name: [asdict(f) for f in findings] for name, findings in report.items()}, sys.stdout, indent=1)
        sys.stdout.write("\n")
        return 0
    for name, findings in report.items():
        if findings:
            sys.stdout.write(f"{name}: {len(findings)} finding(s)\n")
        for f in findings:
            method = f"{f.method}: " if f.method else ""
            sys.stdout.write(f"  {f.file}:{f.line} {f.level} {f.code} {method}{f.message}\n")
    total = sum(len(findings) for findings in report.values())
    sys.stdout.write(f"{len(report)} driver(s) checked, {total} finding(s)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
