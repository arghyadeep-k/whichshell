#!/usr/bin/env sh
# Install whichshell onto PATH.
#
# Usage:
#   curl -fsS https://raw.githubusercontent.com/arghyadeep-k/whichshell/main/install.sh | sh
# or, from a local checkout:
#   ./install.sh
set -eu

REPO_RAW="https://raw.githubusercontent.com/arghyadeep-k/whichshell/main"
DEST_DIR="${WHICHSHELL_INSTALL_DIR:-$HOME/.local/bin}"

SCRIPT_DIR=""
if [ -n "${0:-}" ] && [ "$0" != "sh" ] && [ "$0" != "-" ]; then
    SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" 2>/dev/null && pwd)" || SCRIPT_DIR=""
fi

mkdir -p "$DEST_DIR"

if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/whichshell" ]; then
    cp "$SCRIPT_DIR/whichshell" "$DEST_DIR/whichshell"
else
    if ! command -v curl >/dev/null 2>&1; then
        echo "error: curl is required to install whichshell" >&2
        exit 1
    fi
    curl -fsSL "$REPO_RAW/whichshell" -o "$DEST_DIR/whichshell"
fi

chmod +x "$DEST_DIR/whichshell"

if ! command -v python3 >/dev/null 2>&1; then
    echo "warning: python3 not found on PATH; whichshell requires it to run" >&2
fi

echo "Installed whichshell to $DEST_DIR/whichshell"

case ":$PATH:" in
    *":$DEST_DIR:"*)
        echo "Run: whichshell"
        ;;
    *)
        echo
        echo "$DEST_DIR is not on your PATH. Add this to your shell rc file:"
        echo
        echo "    export PATH=\"$DEST_DIR:\$PATH\""
        echo
        ;;
esac
