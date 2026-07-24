# whichshell

Tells you which shell you're actually running, where its binary lives, and
other relevant details (version, PID/PPID, login/interactive status, config
files found, and how it compares to your `$SHELL` default).

## Install

```sh
curl -fsS https://raw.githubusercontent.com/arghyadeep-k/whichshell/main/install.sh | sh
```

Installs to `~/.local/bin/whichshell`. Requires `python3` (no other
dependencies) and `curl`. Set `WHICHSHELL_INSTALL_DIR` to install elsewhere.

## Usage

```sh
whichshell
```

## Local checkout

```sh
git clone https://github.com/arghyadeep-k/whichshell.git
cd whichshell
./install.sh
```
