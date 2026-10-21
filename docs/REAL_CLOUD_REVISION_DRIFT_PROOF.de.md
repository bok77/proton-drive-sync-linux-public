# Echter Cloud-Revisionswechsel nach Vorschau (20. Oktober 2026)

**Ergebnis: PASS für Cloud-Drift zwischen Vorschau und Freigabe. Release bleibt BLOCKED.**

Geprüft mit der authentifizierten Proton-CLI und ausschließlich der synthetischen Datei `/my-files/ProtonSync-Test/proton-sync-pairing-check.txt` sowie dem isolierten lokalen Testbestand.

1. Lesende Erst-Pairing-Vorschau ergab `READY_FOR_EXPLICIT_APPROVAL` für genau eine identische Testdatei.
2. Danach wurde mittels explizitem `filesystem upload -f create-new-revision -t` eine **geänderte Revision ausschließlich dieser Cloud-Testdatei** erzeugt. Die CLI-Metadaten bestätigten eine andere Revisionskennung und SHA-1-Prüfsumme.
3. Die Freigabe mit der **alten** Vorschau scheiterte erwartungsgemäß an `PAIRING_STALE_OR_CONFLICT`. Eine Baseline wurde nicht angelegt.
4. Der ursprüngliche Dateiinhalt wurde durch eine weitere `create-new-revision`-Operation wiederhergestellt. Readback bestätigte erneut die ursprüngliche SHA-1-Prüfsumme und Größe (104 Byte).
5. Die erneute Pairing-Prüfung ergab `READY_FOR_EXPLICIT_APPROVAL`, matched=1, differences=0, errors=0. Die neue Cloud-Revisionskennung wurde nicht als alte Freigabe akzeptiert.

Regressionstest ergänzt: Auch wenn eine neue Cloud-Revision **identische Bytes** meldet, muss ihre andere Revisionskennung den alten SHA-256-Pairing-Fingerabdruck ungültig machen.

**Grenze:** Weder dieser Test noch die Vor-/Nachprüfung können einen atomaren Snapshot zwischen Linux und Proton Drive garantieren. Nach der letzten Prüfung könnte sich die Cloud erneut ändern. Die neue portable Runtime darf nicht automatisch installiert/aktiviert werden; hierfür sind belastbare Revisions-/Konditionsprüfungen beim tatsächlichen Start und weitere Sicherheitsnachweise erforderlich. Der reale Test erfolgte ausschließlich am Testobjekt, nicht an persönlichen Daten.
