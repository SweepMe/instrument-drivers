"""Tests of tools/check_driver.py for the findings of the modernization pass (DC021 to DC028).

    python -m pytest tests/check_driver

Each test writes a small driver folder into a temporary src/ and checks which codes the checker reports.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import check_driver

YEAR = check_driver._current_year()
COPYRIGHT = f"Copyright (c) 2023-{YEAR} SweepMe! GmbH (sweep-me.net)"
HEADER = f"# MIT License\n#\n# {COPYRIGHT}\n\n"
MODERN = """from __future__ import annotations

from pysweepme import EmptyDevice, debug


class Device(EmptyDevice):
    '''A modern driver.'''

    def update_gui_parameters(self, parameters: dict) -> dict:
        '''The GUI.'''
        return {"Average": parameters.get("Average", 1)}

    def apply_gui_parameters(self, parameters: dict) -> None:
        '''The values.'''
        self.average = parameters.get("Average", 1)

    def configure(self) -> None:
        '''Set up.'''
        debug(self.get_folder("SEQUENCES"))
"""
NEW_CODES = {f"DC0{number}" for number in range(21, 29)}


def write_driver(
    root: Path,
    main: str,
    license_text: str | None = COPYRIGHT,
    *,
    header: str = HEADER,
    encoding: str = "utf-8",
) -> Path:
    """A driver folder src/Driver below root with main.py and, unless None, license.txt."""
    folder = root / "src" / "Driver"
    folder.mkdir(parents=True)
    (folder / "main.py").write_text(header + main, encoding=encoding)
    if license_text is not None:
        (folder / "license.txt").write_text(
            f"MIT License\n\n{license_text}\n\nPermission is hereby granted\n",
            encoding="utf-8",
        )
    return folder


def codes(folder: Path) -> list[str]:
    """The codes of the new findings for a driver folder, in line order."""
    return [f.code for f in check_driver.check_driver(folder) if f.code in NEW_CODES]


def test_modern_driver_is_clean(tmp_path: Path) -> None:
    """A driver after the modernization pass has none of the new findings."""
    assert codes(write_driver(tmp_path, MODERN)) == []


def test_legacy_gui_api_and_indexing(tmp_path: Path) -> None:
    """DC021 for each legacy GUI method, DC022 once per method that indexes the parameters."""
    main = """class Device(EmptyDevice):
    def set_GUIparameter(self):
        return {"Average": 1}

    def get_GUIparameter(self, parameter):
        self.average = parameter["Average"]
        self.mode = parameter["Mode"]
        self.port = parameter.get("Port", "")
"""
    findings = [f for f in check_driver.check_driver(write_driver(tmp_path, main)) if f.code in NEW_CODES]
    assert [f.code for f in findings] == ["DC021", "DC021", "DC022"]
    assert findings[2].level == "warning"
    assert "2 time(s)" in findings[2].message


def test_indexing_in_new_gui_methods(tmp_path: Path) -> None:
    """DC022 also in update_gui_parameters and apply_gui_parameters, whatever the argument is called."""
    main = """class Device(EmptyDevice):
    def update_gui_parameters(self, params):
        return {"Average": params["Average"]}

    def apply_gui_parameters(self, parameters):
        self.average = parameters["Average"]
"""
    assert codes(write_driver(tmp_path, main)) == ["DC022", "DC022"]


def test_ignore_comment_on_gui_method(tmp_path: Path) -> None:
    """A comment above the def accepts DC021 and DC022 of that method."""
    main = """class Device(EmptyDevice):
    # check_driver: ignore DC021, DC022 - kept for a customer script that calls it
    def get_GUIparameter(self, parameter):
        self.average = parameter["Average"]
"""
    assert codes(write_driver(tmp_path, main)) == []


@pytest.mark.parametrize(
    "statement",
    [
        "self.stop_Measurement('no')",
        "self.stop_measurement('no')",
        "self.stopMeasurement = 'no'",
        "self.message_Box('hello')",
        "self.write_Log('hello')",
        "self.message_Info('hello')",
        "self.get_Folder('SELF')",
        "self.is_run_aborted()",
    ],
)
def test_deprecated_calls(tmp_path: Path, statement: str) -> None:
    """DC023 for every deprecated call or assignment."""
    main = f"""class Device(EmptyDevice):
    def configure(self):
        {statement}
"""
    assert codes(write_driver(tmp_path, main)) == ["DC023"]


def test_deprecated_override(tmp_path: Path) -> None:
    """DC023 for an override of find_Ports, which SweepMe! no longer calls; find_ports is fine."""
    main = """class Device(EmptyDevice):
    def find_Ports(self):
        return ["COM1"]

    def find_ports(self):
        return ["COM1"]
"""
    findings = [f for f in check_driver.check_driver(write_driver(tmp_path, main)) if f.code in NEW_CODES]
    assert [(f.code, f.method) for f in findings] == [("DC023", "find_Ports")]


@pytest.mark.parametrize(
    "statement",
    [
        "from EmptyDeviceClass import EmptyDevice",
        "from ErrorMessage import error, debug",
        "import FolderManager",
        "import FolderManager as FoMa",
        "from FolderManager import addFolderToPATH",
    ],
)
def test_legacy_imports(tmp_path: Path, statement: str) -> None:
    """DC024 for a bare import of the modules pysweepme provides."""
    assert codes(write_driver(tmp_path, f"{statement}\n")) == ["DC024"]


@pytest.mark.parametrize(
    "statement",
    [
        "from pysweepme.EmptyDeviceClass import EmptyDevice",
        "from pysweepme.ErrorMessage import error, debug",
        "from pysweepme import FolderManager",
    ],
)
def test_pysweepme_imports_are_fine(tmp_path: Path, statement: str) -> None:
    """The same modules imported from pysweepme are no finding."""
    assert codes(write_driver(tmp_path, f"{statement}\n")) == []


def test_legacy_import_ignored_on_line_above(tmp_path: Path) -> None:
    """Outside a method, the ignore comment stands on the finding's line or the line above."""
    main = "# check_driver: ignore DC024 - a fallback for an old SweepMe!\nfrom ErrorMessage import debug\n"
    assert codes(write_driver(tmp_path, main)) == []


def test_import_inside_method_ignored_on_def(tmp_path: Path) -> None:
    """Inside a method, the ignore comment stands on the def, as for every finding about a method."""
    main = """class Device(EmptyDevice):
    def connect(self):  # check_driver: ignore DC024 - a fallback for an old SweepMe!
        import FolderManager
"""
    assert codes(write_driver(tmp_path, main)) == []


@pytest.mark.parametrize(
    ("key", "expected"),
    [("SETTINGS", ["DC025"]), ("ROAMINGSETTINGS", ["DC025"]), ("SEQUENCES", []), ("CUSTOMFILES", [])],
)
def test_folder_keys(tmp_path: Path, key: str, expected: list[str]) -> None:
    """DC025 for the folder keys that were renamed to ...SEQUENCES."""
    main = f"""class Device(EmptyDevice):
    def configure(self):
        self.folder = self.get_folder("{key}")
"""
    assert codes(write_driver(tmp_path, main)) == expected


@pytest.mark.parametrize(
    ("statement", "expected"),
    [
        ('FoMa.get_path("SETTINGS")', ["DC025"]),
        ('get_path("ROAMINGSETTINGS")', ["DC025"]),
        ('self.get_Folder("SETTINGS")', ["DC025", "DC023"]),
        ('print("SETTINGS")', []),
        ('self.port.write("SETTINGS")', []),
        ('self.lookup = dict(SETTINGS="SETTINGS")', []),
    ],
)
def test_folder_keys_only_in_folder_lookups(tmp_path: Path, statement: str, expected: list[str]) -> None:
    """DC025 only where a folder is looked up by its key, not for the same text in any other call."""
    main = f"""class Device(EmptyDevice):
    def configure(self):
        {statement}
"""
    assert sorted(codes(write_driver(tmp_path, main))) == sorted(expected)


def test_missing_license(tmp_path: Path) -> None:
    """DC026 when license.txt is missing."""
    findings = check_driver.check_driver(write_driver(tmp_path, MODERN, license_text=None))
    assert [(f.code, f.line) for f in findings if f.code in NEW_CODES] == [("DC026", 3)]


def test_license_differs(tmp_path: Path) -> None:
    """DC026 when the copyright lines of the header and license.txt differ."""
    other = f"Copyright (c) 2024-{YEAR} SweepMe! GmbH (sweep-me.net)"
    assert codes(write_driver(tmp_path, MODERN, license_text=other)) == ["DC026"]


def test_license_whitespace_and_case_of_name(tmp_path: Path) -> None:
    """Whitespace inside the line does not count, nor the case of License.txt."""
    folder = write_driver(tmp_path, MODERN, license_text=None)
    (folder / "License.txt").write_text(COPYRIGHT.replace(" ", "  "), encoding="utf-8")
    assert codes(folder) == []


def test_header_without_copyright(tmp_path: Path) -> None:
    """DC026 when main.py has no copyright line in a comment."""
    assert codes(write_driver(tmp_path, MODERN, header="")) == ["DC026"]


def test_outdated_year(tmp_path: Path) -> None:
    """DC027 when the latest year of the copyright lines is below the current year."""
    old = "Copyright (c) 2021-2023 SweepMe! GmbH (sweep-me.net)"
    findings = check_driver.check_driver(write_driver(tmp_path, MODERN, license_text=old, header=f"# {old}\n"))
    assert [f.code for f in findings if f.code in NEW_CODES] == ["DC027"]
    assert f"2021-{YEAR}" in findings[0].message


def test_second_copyright_line_keeps_its_year(tmp_path: Path) -> None:
    """A driver based on another one keeps the original line: only the latest year counts."""
    original = "Copyright (c) 2019 Original Author"
    folder = write_driver(
        tmp_path,
        MODERN,
        license_text=f"{COPYRIGHT}\n{original}",
        header=f"# {COPYRIGHT}\n# {original}\n",
    )
    assert codes(folder) == []


def test_outdated_year_ignored(tmp_path: Path) -> None:
    """The ignore comment for DC027 stands on the copyright line or the line above."""
    old = "Copyright (c) 2021 SweepMe! GmbH (sweep-me.net)"
    header = f"# check_driver: ignore DC027 - no longer maintained\n# {old}\n"
    assert codes(write_driver(tmp_path, MODERN, license_text=old, header=header)) == []


def test_byte_order_mark(tmp_path: Path) -> None:
    """DC028 for a .py file with a UTF-8 byte order mark, which still parses."""
    folder = write_driver(tmp_path, MODERN, encoding="utf-8-sig")
    assert codes(folder) == ["DC028"]
    assert all(f.code != "DC000" for f in check_driver.check_driver(folder))


def test_annotation_escapes_properties() -> None:
    """--github: % first, so a name holding %2C stays itself; then CR, LF, and in properties also : and ,."""
    finding = check_driver.Finding("DC023", "hint", r"src\A%2C,B:C\main.py", 0, "configure", "50% done\r\nnext: a, b")
    expected = "::notice file=src/A%252C%2CB%3AC/main.py,line=1,title=DC023::configure: 50%25 done%0D%0Anext: a, b\n"
    assert check_driver._annotation(finding) == expected


def test_annotation_level() -> None:
    """A warning stays a warning annotation."""
    finding = check_driver.Finding("DC022", "warning", "src/X/main.py", 4, "", "indexed")
    assert check_driver._annotation(finding) == "::warning file=src/X/main.py,line=4,title=DC022::indexed\n"
