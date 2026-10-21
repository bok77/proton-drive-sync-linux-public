# V1 – Ergebnisanzeige für isolierten Einmal-Lauf (21.10.2026)

**Code und isolierter GUI-Startpfad: PASS; echter GUI→Cloud-Transfer: OPEN.**

Der bereits vorhandene Button „Einmaligen Testlauf starten“ zeigt nun eine gesonderte Ergebniszeile an. Beim bestätigten Start merkt sich die Anwendung die aktuelle Zahl der Zeilen der isolierten `state_dir/events.jsonl`; nur spätere `run_end`-Events gelten als Belege. Angezeigt werden `uploaded`, `remote_downloaded`, `conflicts` und `errors`; bei Konflikten und Fehlern wird nicht „erfolgreich“ angezeigt. Ohne neuen Abschluss bleibt der Zustand „Test läuft · Abschluss wird geprüft“ bestehen; die systemd-Startanforderung allein ist kein abgeschlossener Transfer. Fehlende oder nicht interpretierbare Evidenz darf keinen Erfolg ergeben.

Unit-Tests `tests/test_v1_run_result.py` decken stale Events, echte neue Abschlüsse, Konflikte und unvollständige Records ab. Der bestehende Fedora-44-VM-Probe `scripts/probe_v1_mvp_one_shot_vm.py` lief mit aktualisierter GTK-Oberfläche und echtem isoliertem systemd erfolgreich; die Runtime war dabei weiterhin ein **cloudfreier Stub**. Eine echte Anzeige von Upload-/Downloadzählern innerhalb der GUI wurde in diesem VM-Lauf **nicht** bewiesen (der Stub erzeugt kein `run_end`).

**Offene MVP-Grenze:** Die isolierte Voll-Engine ist auf dem Fedora-Host noch nicht als gültiges Paket plus Dienst installiert. Die vorige einmalige Genehmigung für einen direkten CLI-Transfer ist verbraucht und begründet keine allgemeine Freigabe für einen weiteren authentifizierten Cloudlauf. Ein neuer GUI→Cloud-Test benötigt eine erneute, ausdrücklich benannte Scope-Freigabe und technische Vorprüfung. Produktive Dienste dürfen nicht verändert werden. V1 bleibt NOT ACCEPTED.
