# Runtime Separation — Public Alpha Preview (2026-10-21)

The existing desktop launcher remains unchanged, preserving all advanced controls and existing service behavior for its current owner. A new **opt-in**, non-default `--public-alpha` mode creates only an informational overview and settings pane. It intentionally has **no** sync, delete, upload, timer, watcher, routing, or account operations.

This is a defensive separation *foundation*, **not yet a working portable alpha sync client**. The old production GUI must not be shipped as the public default. Before the public package may allow syncing, its isolated adapter needs explicit config selection, installation provenance, integrity checks, scoped service control, and real new-file transfer result evidence without referencing an author's home directory.

The original user-facing settings were not removed or changed by this refactoring. The public preview is opt-in only. Static tests verify its code paths do not dispatch any existing sync callbacks. A direct GTK unit harness segfaulted in the host environment, therefore a fresh graphical-session acceptance proof is still required and is not claimed as passed.
