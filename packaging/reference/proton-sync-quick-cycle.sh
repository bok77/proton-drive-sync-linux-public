#!/usr/bin/env bash
set -uo pipefail
sync_snapshot=$(/usr/bin/python3 "$HOME/.local/bin/proton-sync-queue.py" snapshot)
/usr/bin/python3 "$HOME/.local/bin/proton-bisync-quick.py"
quick_rc=$?
/usr/bin/python3 "$HOME/.local/bin/proton-sync-reconcile.py" --apply
reconcile_rc=$?
if (( quick_rc != 0 || reconcile_rc != 0 )); then
  echo "SYNC_CYCLE_FAILED quick=$quick_rc reconcile=$reconcile_rc" >&2
  exit 1
fi

/usr/bin/python3 "$HOME/.local/bin/proton-sync-queue.py" ack "$sync_snapshot"
