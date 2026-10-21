#!/usr/bin/env bash
set -Eeuo pipefail
for attempt in $(seq 1 120); do
  if mountpoint -q /mnt/example-drive && test -w /mnt/example-sync-root; then
    exec /usr/bin/flock -E 0 -n "$HOME/.local/state/proton-bisync/sync.lock" \
      /usr/bin/python3 "$HOME/.local/bin/proton-cloud-priority.py"
  fi
  sleep 5
done
exit 32
