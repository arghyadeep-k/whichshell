# whichshell

[![CI](https://github.com/arghyadeep-k/whichshell/actions/workflows/ci.yml/badge.svg)](https://github.com/arghyadeep-k/whichshell/actions/workflows/ci.yml)

Tells you which shell you're actually running, where its binary lives, and
other relevant details (version, PID/PPID, login/interactive status, config
files found, and how it compares to your default shell). Works on Linux,
macOS, and Windows (cmd.exe / PowerShell / pwsh).

## Install

**Linux / macOS:**

```sh
curl -fsS https://raw.githubusercontent.com/arghyadeep-k/whichshell/main/install.sh | sh
```

Installs to `~/.local/bin/whichshell`. Requires `python3` (no other
dependencies) and `curl`. Set `WHICHSHELL_INSTALL_DIR` to install elsewhere.

**Windows (cmd.exe or PowerShell):**

```powershell
irm https://raw.githubusercontent.com/arghyadeep-k/whichshell/main/install.ps1 | iex
```

Installs to `%USERPROFILE%\bin` (a `whichshell.py` plus a `whichshell.cmd`
shim so it runs from both cmd.exe and PowerShell) and adds that folder to
your User `PATH`. Requires `python` on PATH, and `powershell` or `pwsh` for
process detection. Set `WHICHSHELL_INSTALL_DIR` to install elsewhere.

## Usage

```sh
whichshell
```

## Local checkout

```sh
git clone https://github.com/arghyadeep-k/whichshell.git
cd whichshell
./install.sh       # Linux/macOS
.\install.ps1       # Windows
```

## Tests

Unit tests cover the detection logic (login/interactive flag parsing for
both POSIX and Windows, CIM JSON parsing, config-file lookup) plus an
end-to-end smoke test that actually runs the CLI. CI runs the suite on
Linux, macOS, and Windows on every push via [GitHub
Actions](.github/workflows/ci.yml) — the Windows job is the only place the
Windows detection path (PowerShell CIM queries, the `.cmd` shim,
`install.ps1`) gets exercised for real, since this was built without
access to a Windows machine.

```sh
python3 -m venv .venv && . .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install pytest
pytest tests/ -v
```
