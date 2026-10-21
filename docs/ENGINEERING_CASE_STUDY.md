# Engineering Case Study – English

## Problem and product decision

Linux users need reliable, privacy-oriented, bidirectional Proton Drive synchronization. The reference project *lafontaj/proton-drive-cli-sync* has a mature but explicitly one-way sync model. Our decision: retain the verified two-way workflow and borrow architectural ideas for file watching, exclusions, and a native GNOME interface.

## Architecture

`inotify → persistent SQLite event queue → guarded systemd unit → verifying synchronization engine → official Proton Drive CLI`

An independent hourly cloud scan and a 10-minute priority scan detect remote changes. The GNOME interface reads metadata and invokes predefined systemd actions only; it does not handle credentials or document contents.

## UX decisions

1. **Tasks first:** clear source, destination, and cadence on the landing view.
2. **Two high-visibility primary actions:** local upload and full bidirectional scan, above diagnostics.
3. **Progressive disclosure:** technical units and run history are behind optional details.
4. **Bilingual:** German and English text for guidance, actions, and errors.
5. **Fail closed:** no assumption that requesting a service proves successful syncing; no permanent auto-deletion.

## Evidence and limits

- Unit tests for positive and negative scenarios, including unavailable services, failed starts, timeouts, and safe configuration handling.
- Prior isolated live tests of the engine included verified upload/download, rename/move, and recoverable cloud trash using dedicated test files.
- No claim of independent external security auditing.
- The synchronization engine remains separately installed and is not yet a portable release.
- Public release approval has not been granted.

## Professional portfolio relevance

The project can demonstrate practical capabilities in stateful distributed workflows, race-aware safety gates, fail-closed design, Linux integration, testing, and bilingual product engineering. It can become a credible technical portfolio artifact, without implying guaranteed visibility or recruitment by large AI providers.

**Next milestone:** portable packaged engine, CI, published synthetic tests, security review, and a privacy-safe GNOME demo.
