#!/usr/bin/env bash
set -euo pipefail
/usr/bin/python3 "$HOME/.local/bin/proton-bisync.py"
/usr/bin/python3 "$HOME/.local/bin/proton-sync-queue.py" clear-full-scan
