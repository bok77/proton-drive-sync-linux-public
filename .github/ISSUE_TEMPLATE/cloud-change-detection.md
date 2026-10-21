---
name: "Cloud change detection / Cloud-Änderungserkennung"
about: "Investigate supported near-real-time changes from Proton Drive"
title: "[Cloud monitor] "
labels: ["community", "enhancement", "research"]
---

## Goal / Ziel
Improve **Proton Drive → Linux** change detection beyond scheduled polling, without weakening two-way sync safety.

## Current behavior / Ist-Zustand
- Local Linux changes use inotify and a fallback timer.
- Selected Proton folders are polled on a configurable schedule.
- The entire cloud is scanned periodically, including folders outside the priority set.
- **No verified server push, SDK changes cursor, or real-time cloud event feed.**

## Community research / Community-Recherche
- [ ] Determine whether current official CLI or SDK has a documented changes feed, cursor or event subscription.
- [ ] Document API support, licensing, authentication, pagination, rate limits and reconnection guarantees.
- [ ] Demonstrate remote create, edit, rename, move, trash, offline recovery and missed events with synthetic data.
- [ ] Preserve an independent full reconciliation fallback and authoritative baseline.
- [ ] Test concurrency, conflict safety, duplicate events, service restarts and access-denied cases.
- [ ] Attach safe reproductions and evidence, not personal cloud metadata.

**Acceptance:** No "real-time" claim without reproducible proof. Changing the cloud detector must not result in lost files or accidental deletions.
