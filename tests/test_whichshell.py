import importlib.util
import os
import stat
import subprocess
import sys
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WHICHSHELL_PATH = REPO_ROOT / "whichshell"


def _load_module():
    loader = SourceFileLoader("whichshell_module", str(WHICHSHELL_PATH))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def ws():
    return _load_module()


# --- detect_posix_flags -----------------------------------------------

def test_posix_login_via_argv0_dash(ws):
    is_login, _ = ws.detect_posix_flags(["-bash"])
    assert is_login is True


def test_posix_login_via_dash_l_flag(ws):
    is_login, _ = ws.detect_posix_flags(["bash", "-l"])
    assert is_login is True


def test_posix_login_via_long_flag(ws):
    is_login, _ = ws.detect_posix_flags(["bash", "--login"])
    assert is_login is True


def test_posix_not_login(ws):
    is_login, _ = ws.detect_posix_flags(["bash"])
    assert is_login is False


def test_posix_interactive_flag(ws):
    _, is_interactive = ws.detect_posix_flags(["bash", "-i"])
    assert is_interactive is True


def test_posix_combined_interactive_flag(ws):
    _, is_interactive = ws.detect_posix_flags(["bash", "-ic", "echo hi"])
    assert is_interactive is True


def test_posix_command_flag_is_noninteractive(ws):
    _, is_interactive = ws.detect_posix_flags(["bash", "-c", "echo hi"])
    assert is_interactive is False


def test_posix_no_signal_is_none(ws):
    _, is_interactive = ws.detect_posix_flags(["bash"])
    assert is_interactive is None


def test_posix_empty_argv(ws):
    is_login, is_interactive = ws.detect_posix_flags([])
    assert is_login is False
    assert is_interactive is None


# --- detect_windows_interactive -----------------------------------------

def test_windows_powershell_noninteractive_flag(ws):
    result = ws.detect_windows_interactive(
        "powershell.exe", ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", "x"]
    )
    assert result is False


def test_windows_powershell_default_interactive(ws):
    result = ws.detect_windows_interactive("powershell.exe", ["powershell.exe"])
    assert result is True


def test_windows_pwsh_noninteractive_case_insensitive(ws):
    result = ws.detect_windows_interactive("pwsh.exe", ["pwsh.exe", "-NonInteractive"])
    assert result is False


def test_windows_cmd_slash_c_is_noninteractive(ws):
    result = ws.detect_windows_interactive("cmd.exe", ["cmd.exe", "/c", "dir"])
    assert result is False


def test_windows_cmd_default_interactive(ws):
    result = ws.detect_windows_interactive("cmd.exe", ["cmd.exe"])
    assert result is True


def test_windows_unknown_shell_is_none(ws):
    result = ws.detect_windows_interactive("someshell.exe", ["someshell.exe"])
    assert result is None


# --- parse_win_cim_json --------------------------------------------------

def test_parse_win_cim_json_full(ws):
    text = (
        '{"Name":"powershell.exe","ExecutablePath":"C:\\\\Windows\\\\System32\\\\'
        'WindowsPowerShell\\\\v1.0\\\\powershell.exe","CommandLine":"powershell.exe -NoLogo",'
        '"ParentProcessId":123}'
    )
    exe_path, argv, ppid = ws.parse_win_cim_json(text)
    assert exe_path.endswith("powershell.exe")
    assert argv == ["powershell.exe", "-NoLogo"]
    assert ppid == 123


def test_parse_win_cim_json_missing_executable_path_falls_back_to_name(ws):
    text = '{"Name":"cmd.exe","ExecutablePath":null,"CommandLine":null,"ParentProcessId":5}'
    exe_path, argv, ppid = ws.parse_win_cim_json(text)
    assert exe_path == "cmd.exe"
    assert argv == ["cmd.exe"]
    assert ppid == 5


def test_parse_win_cim_json_empty_text(ws):
    assert ws.parse_win_cim_json("") == (None, None, None)
    assert ws.parse_win_cim_json(None) == (None, None, None)


def test_parse_win_cim_json_invalid_json(ws):
    assert ws.parse_win_cim_json("not json") == (None, None, None)


# --- find_config_files / find_config_files_windows -----------------------

def test_find_config_files_reports_found_and_missing(ws, tmp_path, monkeypatch):
    (tmp_path / ".bashrc").write_text("")
    (tmp_path / ".bash_profile").write_text("")
    monkeypatch.setattr(ws.os.path, "expanduser", lambda p: p.replace("~", str(tmp_path)))

    results = dict(ws.find_config_files("bash"))
    assert results["~/.bashrc"] is True
    assert results["~/.bash_profile"] is True
    assert results["~/.profile"] is False


def test_find_config_files_unknown_shell_falls_back_to_profile(ws, tmp_path, monkeypatch):
    (tmp_path / ".profile").write_text("")
    monkeypatch.setattr(ws.os.path, "expanduser", lambda p: p.replace("~", str(tmp_path)))

    results = dict(ws.find_config_files("someweirdshell"))
    assert results == {"~/.profile": True}


def test_find_config_files_windows_powershell(ws, tmp_path, monkeypatch):
    profile_dir = tmp_path / "Documents" / "WindowsPowerShell"
    profile_dir.mkdir(parents=True)
    (profile_dir / "Microsoft.PowerShell_profile.ps1").write_text("")
    monkeypatch.setattr(ws.os.path, "expanduser", lambda p: str(tmp_path) if p == "~" else p)

    results = ws.find_config_files_windows("powershell.exe")
    found = {path: exists for path, exists in results}
    assert any(exists for path, exists in results if "WindowsPowerShell" in path)
    assert any(not exists for path, exists in results if path.endswith(
        os.path.join("PowerShell", "Microsoft.PowerShell_profile.ps1")))


def test_find_config_files_windows_unknown_shell_is_empty(ws):
    assert ws.find_config_files_windows("bash") == []


def test_read_cmd_autorun_does_not_raise(ws):
    result = ws.read_cmd_autorun()
    assert result is None or isinstance(result, str)


# --- get_version ----------------------------------------------------------

@pytest.mark.skipif(os.name == "nt", reason="relies on a POSIX shebang script")
def test_get_version_reads_first_line(ws, tmp_path):
    fake_shell = tmp_path / "fake-shell"
    fake_shell.write_text("#!/bin/sh\necho 'FakeShell, version 9.9.9'\necho 'extra line'\n")
    fake_shell.chmod(fake_shell.stat().st_mode | stat.S_IEXEC)

    assert ws.get_version(str(fake_shell)) == "FakeShell, version 9.9.9"


def test_get_version_missing_binary_returns_none(ws):
    assert ws.get_version("/no/such/binary-xyz") is None


def test_get_version_windows_unknown_shell_returns_none(ws):
    assert ws.get_version_windows("C:\\nowhere\\thing.exe", "thing.exe") is None


# --- end-to-end smoke test -------------------------------------------------

def test_cli_runs_and_reports_a_shell():
    result = subprocess.run(
        [sys.executable, str(WHICHSHELL_PATH)],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "Shell:" in result.stdout
    assert "Path:" in result.stdout


def test_cli_help_flag():
    result = subprocess.run(
        [sys.executable, str(WHICHSHELL_PATH), "--help"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout
