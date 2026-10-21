"""Localized strings for Proton Drive Sync. No user data is bundled."""
STRINGS={
"de":{
"app":"Proton Drive Sync","subtitle":"Sicher synchronisieren zwischen Fedora und Proton Drive",
"overview":"Übersicht","activity":"Aktivität","settings":"Einstellungen","status":"Synchronisationsstatus",
"healthy":"Alles aktuell","warning":"Überprüfung erforderlich","unavailable":"Status noch nicht verfügbar",
"health_description":"Überwachung und Schutzmechanismen aktiv","waiting":"Wartende Änderungen",
"tracked":"Synchronisierte Dateien","conflicts":"Konflikte","last_local":"Letzter lokaler Abgleich",
"last_cloud":"Letzter Cloud-Abgleich","local_sync":"Lokale Änderungen","cloud_sync":"Cloud-Änderungen",
"services":"Hintergrunddienste","watcher":"Echtzeit-Dateiwächter","local_timer":"Lokaler Sicherheitsabgleich",
"cloud_timer":"Priorisierte Cloud-Prüfung","full_timer":"Vollständige Cloud-Prüfung",
"health_timer":"Zustandsüberwachung","active":"Aktiv","inactive":"Nicht aktiv",
"refresh":"Aktualisieren","sync_now":"Jetzt abgleichen","requested":"Lokaler Abgleich angefordert",
"cannot_start":"Abgleich konnte nicht gestartet werden","last_events":"Letzte Ereignisse",
"no_events":"Noch keine Ereignisse","exclusions":"Ausschlussregeln","patterns":"Dateimuster",
"directory_names":"Ausgeschlossene Verzeichnisnamen","separated":"Ein Eintrag pro Zeile",
"save":"Speichern","saved":"Regeln gespeichert","save_failed":"Konnte nicht speichern",
"language":"Sprache","system":"System","german":"Deutsch","english":"English",
"safety":"Datenschutz und Sicherheit","safety_hint":"Löschungen kommen nach einer Sicherheitsfrist in den Papierkorb. Endgültiges Löschen bleibt deaktiviert.",
"only_new":"Ausschlüsse gelten nur für neue, noch nicht synchronisierte Dateien.",
"restart_watcher":"Dateiwächter wird nach dem Speichern neu gestartet.",
"details":"Details","path":"Lokaler Ordner","unknown":"Noch kein Lauf","changes":"Änderungen",
"check_now":"Status prüfen","busy":"Wird aktualisiert …","records":"Einträge","errors":"Fehler",
"cloud_priority":"Prioritäts-Cloud-Abgleich","updated":"Zuletzt aktualisiert",
"pending_delete":"Ausstehende Lösch-/Verschiebevorgänge","read_only":"Diese Oberfläche führt keine automatischen Löschungen aus.",
"development":"Lokale Vorschau · Alpha","close":"Schließen","error":"Fehler","success":"Erfolg"},
"en":{
"app":"Proton Drive Sync","subtitle":"Secure synchronization between Fedora and Proton Drive",
"overview":"Overview","activity":"Activity","settings":"Settings","status":"Synchronization status",
"healthy":"Up to date","warning":"Needs attention","unavailable":"Status not available yet",
"health_description":"Monitoring and safety checks enabled","waiting":"Pending changes",
"tracked":"Synced files","conflicts":"Conflicts","last_local":"Last local sync",
"last_cloud":"Last cloud sync","local_sync":"Local changes","cloud_sync":"Cloud changes",
"services":"Background services","watcher":"Real-time file watcher","local_timer":"Local fallback scan",
"cloud_timer":"Priority cloud scan","full_timer":"Full cloud scan",
"health_timer":"Health monitoring","active":"Active","inactive":"Inactive",
"refresh":"Refresh","sync_now":"Sync now","requested":"Local sync requested",
"cannot_start":"Could not start sync","last_events":"Recent events",
"no_events":"No events yet","exclusions":"Exclusion rules","patterns":"File patterns",
"directory_names":"Excluded directory names","separated":"One entry per line",
"save":"Save","saved":"Rules saved","save_failed":"Could not save settings",
"language":"Language","system":"System","german":"Deutsch","english":"English",
"safety":"Privacy and safety","safety_hint":"Deletions move to trash only after a safety delay. Permanent deletion is disabled.",
"only_new":"Exclusions only apply to new files that have not been synced yet.",
"restart_watcher":"The file watcher restarts after you save.",
"details":"Details","path":"Local folder","unknown":"No completed run","changes":"Changes",
"check_now":"Check status","busy":"Refreshing…","records":"Entries","errors":"Errors",
"cloud_priority":"Priority cloud sync","updated":"Last updated",
"pending_delete":"Pending deletes and moves","read_only":"This interface does not perform automatic deletions.",
"development":"Local preview · Alpha","close":"Close","error":"Error","success":"Success"},
}
EVENT_NAMES={
"de":{
"quick_run_end":"Lokaler Abgleich abgeschlossen",
"run_end":"Cloud-Abgleich abgeschlossen",
"priority_run_end":"Prioritätsabgleich abgeschlossen",
"reconcile_run_end":"Verschiebe-/Löschprüfung abgeschlossen",
"quick_uploaded_verified":"Änderung hochgeladen",
"quick_new_uploaded_verified":"Neue Datei hochgeladen",
"priority_downloaded_verified":"Cloud-Datei heruntergeladen",
"reconcile_renamed_verified":"Datei umbenannt oder verschoben",
"reconcile_trashed":"Datei in Papierkorb verschoben",
"conflict":"Konflikt erkannt",
"upload_error":"Upload fehlgeschlagen",
"download_error":"Download fehlgeschlagen",
"cloud_removed_local_quarantined":"Lokale Datei gesichert",
"reconcile_error":"Änderung konnte nicht übernommen werden",
},
"en":{
"quick_run_end":"Local sync completed",
"run_end":"Cloud sync completed",
"priority_run_end":"Priority sync completed",
"reconcile_run_end":"Rename/deletion scan completed",
"quick_uploaded_verified":"Change uploaded",
"quick_new_uploaded_verified":"New file uploaded",
"priority_downloaded_verified":"Cloud file downloaded",
"reconcile_renamed_verified":"File renamed or moved",
"reconcile_trashed":"File moved to trash",
"conflict":"Conflict detected",
"upload_error":"Upload failed",
"download_error":"Download failed",
"cloud_removed_local_quarantined":"Local file quarantined",
"reconcile_error":"Could not apply change",
},
}
def event_label(code,event):
    return EVENT_NAMES[language(code)].get(event,event.replace("_"," ").capitalize())

# Primary actions and synchronization directions are fully localized.
ACTION_TEXT={
"de":{
"source":"Von", "destination":"Nach", "frequency":"Wie oft",
"routes_heading":"Was wird wohin synchronisiert?",
"sync_local_now":"Fedora → Proton jetzt starten",
"sync_full_now":"Proton ↔ Fedora jetzt prüfen",
"sync_local_help":"Lädt lokale Änderungen hoch und prüft Löschungen und Umbenennungen.",
"sync_full_help":"Prüft alle Cloud-Ordner und übernimmt Cloud-Änderungen.",
"started_only":"Angefordert. Der Hintergrunddienst läuft unabhängig weiter; Erfolg unter Aktivität prüfen.",
"route_inactive":"Zeitplan nicht aktiv – bitte Dienst prüfen",
"next_step":"Nächster Schritt",
"all_ready":"Der Abgleich ist eingerichtet. Bei Bedarf kannst du ihn direkt starten.",
"needs_attention":"Ein Dienst benötigt Aufmerksamkeit. Prüfe die Aktivität und Einstellungen.",
"summary":"Synchronisierungsplan",
"manual":"Manueller Abgleich",
"direction":"Richtung",
},
"en":{
"source":"From", "destination":"To", "frequency":"How often",
"routes_heading":"What syncs where?",
"sync_local_now":"Run Fedora → Proton now",
"sync_full_now":"Check Proton ↔ Fedora now",
"sync_local_help":"Uploads local changes and checks deletions and renames.",
"sync_full_help":"Scans all cloud folders and receives cloud-side changes.",
"started_only":"Requested. The background service continues separately; check Activity for the result.",
"route_inactive":"Schedule inactive – check the service",
"next_step":"Next step",
"all_ready":"Sync is configured. You can also start it manually.",
"needs_attention":"A service needs attention. Review Activity and Settings.",
"summary":"Sync plan",
"manual":"Manual synchronization",
"direction":"Direction",
},
}
def action_text(code,key):
    """Return a translated action or route label, never an English-only fallback."""
    return ACTION_TEXT[language(code)][key]

ROUTE_EDITOR_TEXT={
"de":{
"edit":"Bearbeiten", "route_settings":"Synchronisation einstellen",
"local_folder":"Lokaler Ordner", "cloud_folder":"Cloud-Ordner",
"select_folder":"Ordner auswählen", "frequency":"Prüfintervall",
"save_routes":"Änderungen speichern", "route_saved":"Einstellungen übernommen",
"root_locked":"Der Hauptordner ist geschützt. Für den Wechsel ist zuerst eine geprüfte Migration erforderlich.",
"choose_priority":"Cloud-Ordner (je eine Zeile)", "priority_hint":"Unterordner von /my-files. Nur direkte Dateien werden im Kurzintervall geprüft.",
"invalid_folder":"Ordner nicht zulässig oder außerhalb des Synchronisationsbereichs.",
"config_failed":"Einstellungen konnten nicht übernommen werden",
"direct_only":"Bevorzugte Cloud-Ordner", "current_mapping":"Aktive Zuordnung",
"configured":"Konfiguration gespeichert; Zeitplan aktiviert",
"browse":"Durchsuchen …", "fixed_cloud":"Cloud-Hauptordner (geschützt)",
"system_root":"Hauptordner darf ohne Datenmigration nicht geändert werden",
"editable_priority":"Cloud-Ordner hinzufügen oder entfernen",
},
"en":{
"edit":"Edit", "route_settings":"Configure synchronization",
"local_folder":"Local folder", "cloud_folder":"Cloud folder",
"select_folder":"Choose folder", "frequency":"Check interval",
"save_routes":"Save changes", "route_saved":"Settings applied",
"root_locked":"The main folder is protected. A verified migration is required before changing it.",
"choose_priority":"Cloud folders (one per line)", "priority_hint":"Subfolders of /my-files. Only direct files use the shorter interval.",
"invalid_folder":"Invalid folder or outside the synchronized root.",
"config_failed":"Could not apply settings",
"direct_only":"Priority cloud folders", "current_mapping":"Active mapping",
"configured":"Settings saved; schedule activated", "browse":"Browse …",
"fixed_cloud":"Cloud root (protected)",
"system_root":"Root changes require a verified data migration",
"editable_priority":"Add or remove cloud folders",
}}
def route_edit_text(code,key):
    """Return translated route editing instructions without hiding unsupported features."""
    return ROUTE_EDITOR_TEXT[language(code)][key]

def language(code):
    return "de" if code=="de" else "en"
def translate(code,key):
    return STRINGS[language(code)][key]
def validate():
    a=set(STRINGS["de"]);b=set(STRINGS["en"])
    assert a==b,(sorted(a-b),sorted(b-a))
    assert set(ACTION_TEXT["de"])==set(ACTION_TEXT["en"])
    assert set(ROUTE_EDITOR_TEXT["de"])==set(ROUTE_EDITOR_TEXT["en"])
    assert all(value.strip() for pack in STRINGS.values() for value in pack.values())
    return len(a)
