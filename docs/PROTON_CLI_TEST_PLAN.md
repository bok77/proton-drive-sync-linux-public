# Real Proton CLI integration gate (20 October 2026)

STATUS: READ-ONLY PREPARATION ONLY; NO CLOUD WRITES AUTHORIZED.

A second Proton account is **optional**, not required. The existing Proton account may be used exclusively for **read-only** integration inspection of the dedicated synthetic folder `/my-files/ProtonSync-Test`. The local test directory must be separate from `/mnt/example-sync-root` and use a separate private state. The adapter enforces exactly one managed cloud folder, `ProtonSync-Test`, and rejects production local roots.

The test folder and synthetic files must be deliberately created/confirmed by the user before using the test configuration. No real personal documents are to be included. The setup inspector invokes only `filesystem list` for the allowlisted test subtree. It does not upload, download, rename, delete, trash, log in, write a baseline, approve pairing or enable systemd.

IMPORTANT: A folder allowlist in the application is **not a security boundary for the underlying authenticated Proton CLI**; the existing account still has broader privileges if the CLI or invocation is compromised. Therefore **no automated write/delete experiment with the existing account is authorized**. Such tests require separate explicit permission, stronger containment and recoverable synthetic fixtures. For a release, independent install, authentication isolation, race safety, restart, backup and uninstall remain required.

Use a dedicated test account only when stronger account isolation is desired; there is no requirement to maintain a second account indefinitely.
