# M1 – Schutz vor unbedingtem Update bestehender Cloud-Dateien

**Datum:** 21.10.2026 · **Status:** PARTIAL PASS (Code-Gate), M1 und Release bleiben BLOCKED.

Der **portable, noch nicht produktiv verdrahtete** Engine-Code in `src/proton_sync_engine/runtime/proton-bisync.py` und `proton-bisync-quick.py` ruft vor `create-new-revision` die gemeinsame Sicherheitsprüfung `existing_revision_guard.require_atomic_revision_update()` auf. Solange die vorhandene Proton CLI 0.9.0 keine nachgewiesene bedingte Revisionsschreiboperation verfügbar macht, blockiert diese Prüfung mit `conditional_revision_upload_unsupported`. Es wird kein unbedingter Update-Aufruf ausgelöst. Lokal vorhandene Änderungen und die bisherige Baseline bleiben bestehen; ein erfolgreicher Abgleich wird nicht vorgetäuscht.

Der bisherige Regressionstest für die echte Race-Schwachstelle wurde in einen fail-closed-Negativtest geändert. Historische positive Update-Tests mit FakeCloud setzen **ausschließlich im synthetischen Testprozess** eine ausdrücklich gemockte hypothetische atomare Anbieterfähigkeit ein. Dies ist keine reale Anbieterfähigkeit und kein erlaubter Opt-out in Produktion.

**Wichtig:** Die unveränderten, produktiven lokalen Fedora-Binaries und systemd-Units wurden nicht neu installiert und nicht umkonfiguriert. Der Code-Gate ist kein produktiver Hotfix. Neuanlage bisher nicht existierender Cloud-Dateien und konkurrierende gleichzeitige Neuerstellung benötigen ebenfalls einen gesonderten atomaren Ausschluss- oder No-Clobber-Nachweis. Kein offener Cloud-Race-Fall ist durch diesen Teilfix als vollständig gelöst zu betrachten.

**Nächster Gate-Schritt:** Herausfinden, ob der offizielle CLI-/SDK-Vertrag konditionale Uploads bzw. sichere konfliktfreie Create-Only-Operationen anbietet. Ohne diese Fähigkeit muss der sichere Cloud-Schreibpfad weiter eingeschränkt bleiben. Es folgt ein realer, isolierter End-to-End-Nachweis vor einer Produktivumstellung oder einem öffentlichen Alpha-Release.
