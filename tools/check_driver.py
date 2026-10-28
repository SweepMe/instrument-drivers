# ruff: noqa: INP001  # a script in tools/, not a package
"""Check SweepMe! drivers against the driver API and the style guidelines - a work list, not a test.

    python tools/check_driver.py src/SMU-Undalogic_miniSMU-MS01
    python tools/check_driver.py src --json > findings.json

The check reads the source only: it imports no driver (many need vendor libraries), changes nothing and always exits
with 0. Its findings are meant for an agent that works through them and runs the check again; a driver stays valid
without any of them. `warning` marks what is most likely wrong, `hint` what is worth a look.

What it checks follows the driver API (pysweepme @command, Literal, Annotated with Unit, Label and Range) and the
driver guidelines of the sweepme plugin (sweepme-driver-writing, SKILL.md and references/command-declarations.md):

    DC000  a file that cannot be parsed
    DC001  a command parameter without a type annotation
    DC002  a command without a return annotation
    DC003  a parameter compared with fixed strings: a Literal would list them
    DC004  a converted driver: a public method that looks like a command but is not decorated
    DC005  a setter that returns a value (setters and actions return nothing; errors raise)
    DC006  a decorated reader without returns=(...)
    DC007  a command that calls other commands without composite=True
    DC008  a composite command that sends instrument commands itself, without a comment saying why
    DC009  a composite command without the hazards of the commands it calls
    DC010  two setters whose value parameters have the same name (one quantity in two meanings)
    DC011  @command is not the outermost decorator
    DC012  a check of what the annotation already says (@command checks choices and ranges)
    DC013  a "Hazards:" section written into a docstring instead of @command(hazards=...)
    DC014  a semantic function sends an instrument command a communication command also sends
    DC015  the semantic functions are not in the agreed order (the pairs, then the per-point functions)
    DC016  Annotated or Literal written in a signature instead of an alias at module level
    DC017  a `description` class attribute (legacy; the documentation goes into doc/description.md)
    DC018  a command without a docstring
    DC019  a pair of semantic functions (connect/disconnect, ...) split by another method
    DC020  a setter's value parameter named generically (value, state, mode, ...) instead of after its quantity

Only the .py files directly in a driver folder are read (main.py and the helper modules beside it, not libraries).

A finding that is deliberate is accepted with a comment on the method (on a decorator or the def line, or the line
above them) or, for a finding about the file, on its line or the line above, saying why:

    # check_driver: ignore DC004 - a helper of the semantic functions, not a command
"""

from __future__ import annotations

import argparse
import ast
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
    "apply_selectors", "forget_selections",
)
#: A public method whose name starts like this looks like a command.
COMMAND_PREFIXES = ("get_", "set_", "read_", "write_", "measure_", "fetch_", "enable_", "disable_", "start_", "stop_",
                    "reset", "trigger", "abort", "clear_", "is_")
CHANNEL_PARAMETERS = ("channel",)
#: Value parameter names that say nothing about the quantity a setter sets (DC020): renamed when a driver is touched.
GENERIC_VALUE_NAMES = ("value", "val", "state", "mode", "setting", "x", "v")
#: A comment accepting a finding where it is deliberate: "# check_driver: ignore DC004, DC010 - why".
IGNORE = re.compile(r"#\s*check_driver:\s*ignore\s+((?:DC\d{3}[,\s]*)+)", re.IGNORECASE)
PORT_METHODS = ("write", "query", "read", "write_raw", "read_raw")
#: What is most likely wrong; every other code is a hint.
WARNINGS = {"DC000", "DC001", "DC002", "DC005", "DC006", "DC007", "DC011"}


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
    decorated: bool = False
    composite: bool = False
    has_returns: bool = False
    hazards: bool = False
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
    methods: dict[str, Method] = field(default_factory=dict)
    order: list[tuple[str, str, int]] = field(default_factory=list)  # (file, name, line) in definition order
    checked_aliases: set[str] = field(default_factory=set)  # aliases with a Literal or a Range inside
    description_attributes: list[tuple[str, int]] = field(default_factory=list)
    unreadable: list[tuple[str, int, str]] = field(default_factory=list)

    @property
    def declared(self) -> bool:
        """Whether the driver uses @command (then only decorated methods are commands)."""
        return any(m.decorated for m in self.methods.values())


@dataclass
class Report:
    """The findings of one driver."""

    findings: list[Finding] = field(default_factory=list)

    def add(self, code: str, method: Method | None, line: int, message: str, file: str = "") -> None:
        """Note one finding; its level follows from the code."""
        level = "warning" if code in WARNINGS else "hint"
        self.findings.append(Finding(code, level, file or (method.file if method else ""), line,
                                     method.name if method else "", message))


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
    return text.strip().split(" ")[0].split("?")[0].upper()


def _uses_names(node: ast.AST) -> set[str]:
    """Every plain name used in an expression."""
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _method(node: ast.FunctionDef, file: str, path: Path) -> Method:
    """A method with what its decorators and its body say."""
    method = Method(node.name, node, file, path)
    for decorator in node.decorator_list:
        if _decorator_name(decorator) == "command":
            method.decorated = True
            composite = _keyword(decorator, "composite")
            method.composite = isinstance(composite, ast.Constant) and composite.value is True
            method.has_returns = _keyword(decorator, "returns") is not None
            method.hazards = _keyword(decorator, "hazards") is not None
            kind = _keyword(decorator, "kind")
            method.kind_run = isinstance(kind, ast.Constant) and kind.value == "run"
    for sub in ast.walk(node):
        if not (isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute)):
            continue
        owner = sub.func.value
        if isinstance(owner, ast.Name) and owner.id == "self":
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
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if isinstance(item, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "description"
                                                    for t in item.targets):
                driver.description_attributes.append((file, item.lineno))
            if isinstance(item, ast.FunctionDef):
                driver.methods[item.name] = _method(item, file, path)
                driver.order.append((file, item.name, item.lineno))


def read_driver(folder: Path) -> Driver:
    """Collect the classes' methods and the module-level aliases of a driver folder."""
    driver = Driver(folder)
    trees = []
    for path in sorted(folder.glob("*.py")):
        file = str(path.relative_to(folder.parent.parent)) if folder.parent.parent in path.parents else str(path)
        try:
            tree = _parse(path)
        except (SyntaxError, UnicodeDecodeError) as exc:
            driver.unreadable.append((file, getattr(exc, "lineno", 0) or 0, str(exc)))
            continue
        trees.append(tree)
        _read_module(tree, file, path, driver)
    # an alias built on an alias that has a choice or a range has it too
    for tree in trees:
        for node in tree.body:
            if (isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                    and _uses_names(node.value) & driver.checked_aliases):
                driver.checked_aliases.add(node.targets[0].id)
    return driver


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
    command_names = {m.name for m in commands}
    for method in commands:
        _check_command(method, driver, command_names, report)

    if driver.declared:
        for method in driver.methods.values():
            if not method.decorated and _is_command_like(method):
                report.add("DC004", method, method.node.lineno,
                           "looks like a command but is not decorated - in a driver using @command it is not offered")
        _duplicate_quantities(commands, report)
    _generic_value_names(commands, report)
    _semantic_raw_commands(driver, commands, report)
    _semantic_order(driver, report)
    _split_pairs(driver, report)
    for file, line in driver.description_attributes:
        report.add("DC017", None, line,
                   "a `description` class attribute - write the documentation into doc/description.md", file)
    return sorted((f for f in report.findings if not _ignored(f, driver)), key=lambda f: (f.file, f.line, f.code))


def _ignored(finding: Finding, driver: Driver) -> bool:
    """Whether a comment accepts the finding.

    It stands on the method's decorators or def line or in the comment block right above them, or for a finding about
    the file on the finding's line or the line above.
    """
    method = driver.methods.get(finding.method) if finding.method else None
    if method is not None and method.file == finding.file:
        first = method.node.lineno - len(method.node.decorator_list) - 1
        last = method.node.body[0].lineno - 1 if method.node.body else method.node.lineno
        path = method.path
    else:
        first, last = finding.line - 1, finding.line
        path = next((m.path for m in driver.methods.values() if m.file == finding.file), None)
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
            _LINES[path] = path.read_text(encoding="utf-8-sig").splitlines()
        except OSError:
            _LINES[path] = []
    return _LINES[path]


def _check_command(method: Method, driver: Driver, command_names: set[str], report: Report) -> None:
    """The checks of one command: annotations, docstring, what it returns, composite, decorator order."""
    node = method.node
    for parameter in method.parameters:
        if parameter.annotation is None:
            report.add("DC001", method, node.lineno, f"parameter '{parameter.arg}' has no type annotation")
        elif ast.unparse(parameter.annotation).startswith(("Annotated[", "Literal[")):
            report.add("DC016", method, node.lineno,
                       f"'{parameter.arg}' is annotated inline - define an alias for it at module level")
    if node.returns is None:
        report.add("DC002", method, node.lineno, "no return annotation (-> None for a setter or an action)")
    docstring = ast.get_docstring(node)
    if not docstring:
        report.add("DC018", method, node.lineno, "no docstring")
    elif re.search(r"^\s*Hazards?:", docstring, re.MULTILINE) and not method.hazards:
        report.add("DC013", method, node.lineno,
                   "a Hazards section in the docstring - say it in @command(hazards=...), which adds the section")
    if method.decorated and node.returns is not None and not method.returns_none and not method.has_returns:
        report.add("DC006", method, node.lineno,
                   "a reader without returns=(...) - the driver does not load (pysweepme raises a TypeError)")
    if method.name.startswith("set_") or (method.decorated and method.returns_none):
        _returned_value(method, report)
    if method.decorated and _decorator_name(node.decorator_list[0]) != "command":
        report.add("DC011", method, node.lineno,
                   "@command is not the outermost decorator - a decorator above it may drop the marker")
    _composite(method, driver, command_names, report)
    _redundant_checks(method, driver, report)
    _literal_candidates(method, report)


def _returned_value(method: Method, report: Report) -> None:
    """DC005: a setter or an action that returns something."""
    for sub in ast.walk(method.node):
        if isinstance(sub, ast.Return) and sub.value is not None and not (
                isinstance(sub.value, ast.Constant) and sub.value.value is None):
            report.add("DC005", method, sub.lineno,
                       "returns a value - a setter or action returns nothing and raises when something is wrong; "
                       "what it produced is read with a getter")
            return


def _composite(method: Method, driver: Driver, command_names: set[str], report: Report) -> None:
    """DC007, DC008, DC009: a command that calls commands, and what a composite one does itself."""
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
    if not method.hazards:
        hazardous = sorted(c for c in called if driver.methods.get(c) and driver.methods[c].hazards)
        if hazardous:
            report.add("DC009", method, method.node.lineno,
                       f"calls commands with hazards ({', '.join(hazardous)}) but declares none itself")


def _commented(method: Method) -> bool:
    """Whether the method, or the lines right above it, carry a comment (a reason for sending commands itself)."""
    lines = _lines(method.path)
    start = method.node.lineno - 1 - len(method.node.decorator_list) - 3
    end = method.node.end_lineno or method.node.lineno
    return any("#" in line for line in lines[max(start, 0):end])


def _redundant_checks(method: Method, driver: Driver, report: Report) -> None:
    """DC012: an if that raises on a parameter whose annotation already states the choices or the range."""
    if not method.decorated:
        return
    checked = {p.arg for p in method.parameters
               if p.annotation is not None and (_uses_names(p.annotation) & driver.checked_aliases
                                                or ast.unparse(p.annotation).startswith("Literal["))}
    for sub in ast.walk(method.node):
        if (checked and isinstance(sub, ast.If) and _uses_names(sub.test) & checked
                and any(isinstance(n, ast.Raise) for n in sub.body)
                and isinstance(sub.test, (ast.Compare, ast.UnaryOp, ast.BoolOp))):
            names = ", ".join(sorted(_uses_names(sub.test) & checked))
            report.add("DC012", method, sub.lineno,
                       f"checks {names} although its annotation states the choices or range - @command checks them")
            return


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


def _duplicate_quantities(commands: list[Method], report: Report) -> None:
    """DC010: setters whose value parameters share a name, so two quantities would share one recorded series."""
    owners: dict[str, list[Method]] = {}
    for method in commands:
        if not method.returns_none or method.kind_run or method.composite:
            continue
        for parameter in method.parameters:
            if parameter.arg not in CHANNEL_PARAMETERS:
                owners.setdefault(parameter.arg, []).append(method)
    for name, methods in sorted(owners.items()):
        if len(methods) > 1:
            listed = ", ".join(m.name for m in methods)
            report.add("DC010", methods[1], methods[1].node.lineno,
                       f"the value parameter '{name}' is set by {listed} - name each after what it sets, "
                       f"or they are one quantity in the recorded values")


def _generic_value_names(commands: list[Method], report: Report) -> None:
    """DC020: a setter's value parameter named `value`, `state`, `mode`, ... - the recorded series takes its name.

    A setter is a method annotated -> None, or in an undeclared driver one named set_...; the renaming break is
    accepted whenever a driver is touched (Driver API concept, review point 4).
    """
    for method in commands:
        if method.kind_run or method.composite:
            continue
        if not (method.returns_none or (not method.decorated and method.name.startswith("set_"))):
            continue
        for parameter in method.parameters:
            if parameter.arg.lower() in GENERIC_VALUE_NAMES:
                report.add("DC020", method, method.node.lineno,
                           f"the value parameter '{parameter.arg}' does not say what it sets - name it after its "
                           f"quantity (voltage, operation_mode, current_range), which names the recorded series")


def _semantic_raw_commands(driver: Driver, commands: list[Method], report: Report) -> None:
    """DC014: a semantic function sends an instrument command that a communication command also sends."""
    wrapped: dict[str, str] = {}
    for method in commands:
        for _, head in method.port_heads:
            if head:
                wrapped.setdefault(head, method.name)
    for name in SEMANTIC_ORDER:
        method = driver.methods.get(name)
        for line, head in method.port_heads if method else ():
            if head in wrapped:
                report.add("DC014", method, line, f"sends '{head}' itself, which {wrapped[head]}() also sends - "
                                                    f"call it where it does the same")


def _semantic_order(driver: Driver, report: Report) -> None:
    """DC015: the semantic functions of a file in the agreed order (SEMANTIC_ORDER)."""
    by_file: dict[str, list[tuple[int, str]]] = {}
    for file, name, line in driver.order:
        if name in SEMANTIC_ORDER:
            by_file.setdefault(file, []).append((line, name))
    for file, defined in by_file.items():
        names = [name for _, name in sorted(defined)]
        expected = sorted(names, key=SEMANTIC_ORDER.index)
        if names != expected:
            first = next(i for i, (a, b) in enumerate(zip(names, expected, strict=True)) if a != b)
            report.add("DC015", None, sorted(defined)[first][0],
                       f"semantic functions out of order: {', '.join(names)} - expected "
                       f"{', '.join(expected)}", file)


def _split_pairs(driver: Driver, report: Report) -> None:
    """DC019: an opener and its closer (connect/disconnect, ...) with another method defined between them."""
    for file in {file for file, _, _ in driver.order}:
        names = [name for f, name, _ in sorted(driver.order, key=lambda item: item[2]) if f == file]
        lines = {name: line for f, name, line in driver.order if f == file}
        for opener, closer in PAIRS:
            if opener in names and closer in names and names.index(closer) != names.index(opener) + 1:
                report.add("DC019", None, lines[closer],
                           f"{closer} does not directly follow {opener} - keep the pair together", file)


# --- command line ------------------------------------------------------------------------------------------------

def driver_folders(paths: list[str]) -> list[Path]:
    """The driver folders named, or every driver folder below a folder like src."""
    folders: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if (path / "main.py").is_file():
            folders.append(path)
        elif path.is_dir():
            folders.extend(sorted(p for p in path.iterdir() if (p / "main.py").is_file()))
        else:
            sys.stderr.write(f"not a driver folder: {path}\n")
    return folders


def main(argv: list[str] | None = None) -> int:
    """Check the drivers named on the command line and write the findings to stdout."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("paths", nargs="+", help="driver folders, or a folder holding driver folders (e.g. src)")
    parser.add_argument("--json", action="store_true", help="write the findings as JSON, for an agent")
    parser.add_argument("--only", default="", help="comma-separated codes to report, e.g. DC005,DC010")
    parser.add_argument("--warnings", action="store_true", help="report warnings only, no hints")
    args = parser.parse_args(argv)

    only = {code.strip().upper() for code in args.only.split(",") if code.strip()}
    report = {folder.name: [f for f in check_driver(folder)
                            if (not only or f.code in only) and (not args.warnings or f.level == "warning")]
              for folder in driver_folders(args.paths)}

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
