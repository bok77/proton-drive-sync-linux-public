#!/usr/bin/env bash
set -Eeuo pipefail
case "${1:-}" in
  quick) script="$HOME/.local/bin/proton-sync-quick-cycle.sh";;
  full) script="$HOME/.local/bin/proton-sync-full-cycle.sh";;
  *) echo "Usage: $0 quick|full" >&2; exit 64;;
esac
for attempt in $(seq 1 120); do
  if mountpoint -q /mnt/example-drive && test -w /mnt/example-sync-root; then
    mkdir -p "$HOME/.local/state/proton-bisync"
    # A full scan MUST run after competing short scans, never report a false
    # success due to a busy lock. Quick checks may skip and retry next tick.
    # If the full scan cannot obtain the lock in 30 minutes, exit non-zero.
    if [[ "${1:-}" == full ]]; then
      exec /usr/bin/flock -E 75 -w 1800 "$HOME/.local/state/proton-bisync/sync.lock" "$script"
    fi
    exec /usr/bin/flock -E 0 -n "$HOME/.local/state/proton-bisync/sync.lock" "$script"
  fi
  if (( attempt == 1 || attempt % 12 == 0 )); then
    printf '%s WAIT /mnt/example-drive mount attempt=%s/120\n' "$(date -Is)" "$attempt"
  fi
  sleep 5
done
echo "ERROR: /mnt/example-drive unavailable after 10 minutes" >&2
exit 32
