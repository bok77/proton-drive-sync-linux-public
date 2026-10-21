# M1: Neuerstellungs-Race mit Proton CLI 0.9.0 – Teststand 21.10.2026

**Synthetischer Teiltest PASS; reale providerseitige Atomizität UNBESTÄTIGT; M1 weiterhin BLOCKED.**

Die lokal installierte offizielle Proton Drive CLI (`cli-drive@0.9.0`, SDK `js@0.22.2`) listet für `filesystem upload` Konfliktstrategien `create-new-revision`, `rename`, `replace`, `skip` auf. `skip` beschreibt das Überspringen vorhandener kollidierender Dateien; es ist **kein ausdrückliches dokumentiertes serverseitiges Compare-and-Swap/If-None-Match-Versprechen**.

Der portable Full-Sync und Quick-Sync nutzen bei Neuanlage bereits `filesystem upload -f skip`. Der neue deterministische Test `tests/test_mvp_concurrent_new_file.py` injiziert genau beim Upload eine gleichzeitige Neuerstellung im simulierten Cloud-Backend: Ergebnis der korrigierten Fake-CLI ist Fehler/kein Upload, die neuere Remote-Datei und der lokale Inhalt bleiben unverändert, die Baseline wird nicht um den Konfliktpfad erweitert. Die bisherige FakeCloud hatte zuvor irrtümlich das fünfte statt des vierten CLI-Arguments als Strategie interpretiert; dieser Testmodellfehler wurde korrigiert.

**Sicherheitsgrenze:** Dieses Testergebnis beweist nur den eigenen Engine-Ablauf *unter angenommener CLI-skip-Semantik*. Ob `skip` atomar genug ist, um denselben Namen bei parallelen realen Cloud-Aktionen nicht versehentlich zu überschreiben, ist in der CLI-Hilfe nicht belegt. Ebenso ist bei gleichzeitiger `create-folder`-Operation noch kein gleichwertiger Nachweis vorhanden. Bis zum kontrollierten echten CLI-Test und einem belastbaren Provider-Vertrag bleibt das produktive/öffentliche Write-Gate gesperrt. Für bestehende Dateien bleibt der bereits eingeführte fail-closed Guard unverändert.

Keine produktiven Proton-Daten, Authentifizierungstokens oder systemd-Units wurden für diesen Nachweis angesprochen oder verändert.
