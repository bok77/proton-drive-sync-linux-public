"""GNOME setup for isolated test-folder pairing; no sync activation.

Actual pairing is possible only after an explicit exact-match read-only
inventory and typed consent. No background services are installed or started.
"""
from __future__ import annotations

from gi.repository import Adw,Gtk,GLib
from .cli_error_labels import safe_pairing_error
import threading
from pathlib import Path

COPY={
"de":{
"title":"Proton Drive einrichten",
"intro":"Schritt für Schritt zur sicheren Verbindung von Linux und Proton Drive.",
"status":"V1-Pilot · nur Testordner · Updates bestehender Cloud-Dateien aus Sicherheitsgründen gesperrt",
"one":"1  Speicherorte festlegen",
"local":"Lokaler Ordner",
"cloud":"Proton Drive",
"folder":"Wird bei der späteren Installation ausgewählt",
"cloudpath":"/my-files/ProtonSync-Test – ausschließlich lesend",
"two":"2  Dateien vergleichen",
"compare":"Bestände prüfen",
"compare_info":"Die Einrichtung prüft Dateien, Größen und Prüfsummen. Abweichungen bleiben Konflikte. V1 kann neue Testdateien übertragen, aber bestehende Cloud-Dateien nicht aktualisieren.",
"three":"3  Ergebnis überprüfen",
"empty":"Noch keine Prüfung ausgeführt",
"table_head":"Was vor der Freigabe sichtbar wird:",
"matching":"Identische Dateien und ihre geprüften Revisionen",
"missing":"Dateien, die nur auf einer Seite existieren",
"conflict":"Dateien mit unterschiedlichem Inhalt und Fehler",
"four":"4  Verbindung ausdrücklich bestätigen",
"blocked":"Nur Testordner: Pairing kann bestätigt werden. Synchronisierungsdienste bleiben deaktiviert.",
"confirm":"Exaktes Erst-Pairing bestätigen",
"demo":"Testbestand lesend prüfen",
"demo_title":"Echte lesende Testprüfung",
"demo_body":"12 identische Dateien · 1 Datei nur auf Linux · 1 Datei nur in Proton Drive · 1 Konflikt.\n\nErgebnis: BLOCKED. Es wurde nichts verändert.",
},
"en":{
"title":"Set up Proton Drive",
"intro":"Connect Linux and Proton Drive safely, one verified step at a time.",
"status":"V1 pilot · test folder only · updates to existing cloud files are blocked for safety",
"one":"1  Choose storage locations",
"local":"Local folder",
"cloud":"Proton Drive",
"folder":"Selected during future setup",
"cloudpath":"/my-files/ProtonSync-Test – read-only only",
"two":"2  Compare files",
"compare":"Review both sides",
"compare_info":"Setup checks files, sizes and checksums. Differences remain conflicts. V1 can transfer new test files but cannot update existing cloud files.",
"three":"3  Review the results",
"empty":"No scan has been run",
"table_head":"Before approval, you will see:",
"matching":"Identical files and verified revisions",
"missing":"Files present on one side only",
"conflict":"Mismatched content and errors",
"four":"4  Confirm pairing explicitly",
"blocked":"Test folder only: pairing may be confirmed; sync services remain disabled.",
"confirm":"Approve exact initial pairing",
"demo":"Inspect test account read-only",
"demo_title":"Actual read-only test inventory",
"demo_body":"12 identical files · 1 Linux-only file · 1 Proton-only file · 1 conflict.\n\nOutcome: BLOCKED. No data was modified.",
}
}

def verified_isolated_pairing():
    """Hide obsolete pairing controls only for an already verified test setup."""
    from pathlib import Path
    import json
    config=Path.home()/".config/proton-sync-isolated/config.json"
    try:
        if config.is_symlink() or config.stat().st_mode & 0o077:
            return False
        data=json.loads(config.read_text())
        if data.get("managed_folders") != ["ProtonSync-Test"]:
            return False
        state=Path(data["state_dir"])
        if state.is_symlink() or state.stat().st_mode & 0o077:
            return False
        return ((state/"initial_pairing_verified.json").read_text()
                == "INITIAL_PAIRING_VERIFIED_V1"
                and not (state/"initial_pairing_pending.json").exists())
    except (OSError,ValueError,KeyError,TypeError):
        return False

def make_page(language:str):
    t=COPY["de" if language=="de" else "en"]
    body=Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=14)
    for side in ("top","bottom","start","end"):
        getattr(body,"set_margin_"+side)(18)
    heading=Gtk.Label(label=t["title"],xalign=0)
    heading.add_css_class("page-heading")
    body.append(heading)
    intro=Gtk.Label(label=t["intro"],xalign=0,wrap=True)
    body.append(intro)
    status=Gtk.Label(label=t["status"],xalign=0,wrap=True)
    status.add_css_class("muted")
    body.append(status)

    def group(title):
        g=Adw.PreferencesGroup(title=title)
        body.append(g)
        return g

    locations=group(t["one"])
    locations.add(Adw.ActionRow(title=t["local"],subtitle=t["folder"]))
    locations.add(Adw.ActionRow(title=t["cloud"],subtitle=t["cloudpath"]))
    check=group(t["two"])
    explain=Adw.ActionRow(title=t["compare"],subtitle=t["compare_info"])
    check.add(explain)
    results=group(t["three"])
    state=Adw.ActionRow(title=t["empty"],subtitle=t["table_head"])
    results.add(state)
    for key in ("matching","missing","conflict"):
        results.add(Adw.ActionRow(title=t[key]))
    config_entry=Gtk.Entry()
    config_entry.set_placeholder_text("Test config JSON (0600)")
    body.append(config_entry)
    demo=Gtk.Button(label=t["demo"])
    review_state={"review":None,"config":None}
    approval_entry=Gtk.Entry()
    approval_entry.set_placeholder_text("I APPROVE EXACT INITIAL PAIRING")
    approval_entry.set_tooltip_text("Exact manual consent; only the dedicated synthetic ProtonSync-Test folder is permitted")
    button=Gtk.Button(label=t["confirm"])
    button.set_sensitive(False)
    def update_approval(*_):
        from proton_sync_engine.pairing import APPROVAL
        button.set_sensitive(
            review_state["review"] is not None
            and review_state["review"].get("status")=="READY_FOR_EXPLICIT_APPROVAL"
            and config_entry.get_text().strip()==review_state["config"]
            and approval_entry.get_text()==APPROVAL)
    approval_entry.connect("changed",update_approval)
    config_entry.connect("changed",lambda *_: (review_state.update(review=None),update_approval()))
    demo.add_css_class("suggested-action")
    def example(*_):
        path=config_entry.get_text().strip()
        if not path:
            state.set_title("Separate test configuration required")
            state.set_subtitle("Select an explicit private test configuration JSON file.")
            return
        review_state["review"]=None
        button.set_sensitive(False)
        demo.set_sensitive(False)
        state.set_title("Reading actual test inventory …")
        state.set_subtitle("")
        def deliver(result=None,error=None):
            demo.set_sensitive(True)
            if error:
                state.set_title("BLOCKED")
                state.set_subtitle(safe_pairing_error(error,language))
                return False
            review_state.update(review=result,config=path)
            update_approval()
            state.set_title("Read-only pairing inspection")
            state.set_subtitle(
                f"{result['matched']} identical · "
                f"{len(result['differences'])} differences · "
                f"{len(result['errors'])} errors · {result['status']}")
            for row in result["differences"]:
                results.add(Adw.ActionRow(
                    title=str(row.get("path",""))[:160],
                    subtitle=str(row.get("reason",""))[:160]))
            for row in result["errors"]:
                results.add(Adw.ActionRow(
                    title="Cloud inventory blocked",
                    subtitle=safe_pairing_error(row.get("reason"),language)))
            return False
        def work():
            try:
                from proton_sync_engine.test_cloud_adapter import inspect
                GLib.idle_add(deliver,inspect(path),None)
            except Exception as exc:
                GLib.idle_add(deliver,None,str(exc))
        threading.Thread(target=work,daemon=True).start()
    demo.connect("clicked",example)
    body.append(demo)
    approval=group(t["four"])
    approval.add(Adw.ActionRow(title=t["blocked"]))
    approval.add(Adw.ActionRow(title="Exact consent",subtitle="Only if the test inventory is identical; creates baseline but starts no sync service"))
    body.append(approval_entry)
    def approve_clicked(*_):
        review=review_state["review"]
        path=config_entry.get_text().strip()
        from proton_sync_engine.pairing import APPROVAL
        if (review is None or review.get("status")!="READY_FOR_EXPLICIT_APPROVAL"
            or path!=review_state["config"] or approval_entry.get_text()!=APPROVAL):
            button.set_sensitive(False)
            return
        button.set_sensitive(False)
        demo.set_sensitive(False)
        state.set_title("Rechecking and approving exact pairing …")
        def completed(result=None,error=None):
            demo.set_sensitive(True)
            review_state["review"]=None
            approval_entry.set_text("")
            button.set_sensitive(False)
            state.set_title("PAIRING BLOCKED" if error else "PAIRING RECORDED — NOT ACTIVATED")
            state.set_subtitle(safe_pairing_error(error,language) if error else "Baseline and pending guard stored; no transfer and no service start")
            return False
        def worker():
            try:
                from proton_sync_engine.test_cloud_adapter import TestCloudAdapter
                from proton_sync_engine.installer_pairing import approve_pairing
                result=approve_pairing(Path(path),TestCloudAdapter(path),review,APPROVAL)
                GLib.idle_add(completed,result,None)
            except Exception as exc:
                GLib.idle_add(completed,None,str(exc))
        from pathlib import Path
        threading.Thread(target=worker,daemon=True).start()
    button.connect("clicked",approve_clicked)
    body.append(button)
    if verified_isolated_pairing():
        # Pairing has already passed its one-time guard; do not invite a repeat.
        for obsolete in (locations,check,results,config_entry,demo,approval,approval_entry,button):
            body.remove(obsolete)
        status.set_text("Erstverbindung abgeschlossen · Testordner verifiziert" if language=="de"
                        else "Initial pairing complete · test folder verified")
        config_entry.set_text(str(Path.home()/".config/proton-sync-isolated/config.json"))
    # These controls exclusively manage the isolated synthetic MVP units, not production sync.
    service_group=group("5  Isolierten Testdienst verwalten" if language=="de" else "5  Manage isolated test service")
    service_group.add(Adw.ActionRow(
        title="Nur Testbetrieb · ProtonSync-Test" if language=="de" else "Test mode only · ProtonSync-Test",
        subtitle=("Dieser Dienst ist vom regulären Proton-Abgleich getrennt. Installation startet keine Synchronisierung."
                  if language=="de" else "Separate from normal Proton synchronization. Installation never starts a sync.")))
    service_info=Adw.ActionRow(title="Status wird geprüft …" if language=="de" else "Checking status …")
    service_group.add(service_info)
    service_note=Gtk.Label(xalign=0,wrap=True)
    service_note.add_css_class("muted")
    body.append(service_note)
    primary=Gtk.Button()
    primary.add_css_class("suggested-action")
    body.append(primary)
    secondary=Gtk.Button()
    body.append(secondary)
    service_busy={"value":False}
    service_state={"status":None,"primary":None,"secondary":None}
    actions={
        "install":("Dienst installieren","Install test service"),
        "enable":("Testdienst aktivieren","Enable test service"),
        "pause":("Testdienst pausieren","Pause test service"),
        "uninstall":("Testdienst entfernen","Remove test service"),
    }
    descriptions={
        "install":("Installiert nur die beiden isolierten systemd-Units. Es wird nichts gestartet.",
                   "Installs only the isolated systemd units. Nothing starts."),
        "enable":("Aktiviert ausschließlich den isolierten Test-Timer für ProtonSync-Test. Der normale Abgleich bleibt unverändert.",
                  "Enables only the isolated ProtonSync-Test timer. Normal sync stays unchanged."),
        "pause":("Stoppt und deaktiviert ausschließlich den isolierten Test-Timer.",
                 "Stops and disables only the isolated test timer."),
        "uninstall":("Entfernt nur die isolierten Test-Units. Testkonfiguration und Daten bleiben bestehen.",
                     "Removes only the isolated test units. Configuration and data remain."),
    }
    def localized(pair):
        return pair[0] if language=="de" else pair[1]
    def display_status(result):
        status=result["status"]
        service_state["status"]=status
        if status in ("NOT_INSTALLED","UNINSTALLED"):
            title=("Nicht installiert","Not installed")
            service_state.update(primary="install",secondary=None)
        elif status in ("INSTALLED_NOT_ENABLED","INSTALLED") and not result.get("timer_enabled",False):
            title=("Installiert · nicht aktiv","Installed · inactive")
            service_state.update(primary="enable",secondary="uninstall")
        elif status=="INSTALLED" and result.get("timer_enabled") and result.get("timer_active"):
            title=("Testdienst aktiv","Test service running")
            service_state.update(primary="pause",secondary="uninstall")
        else:
            title=("Zustand unklar · keine Aktion möglich","Unclear state · actions blocked")
            service_state.update(primary=None,secondary=None)
        service_info.set_title(localized(title))
        service_info.set_subtitle("Isolierter Testdienst – nicht die bestehende Synchronisierung" if language=="de"
                                  else "Isolated test service – not your existing synchronization")
        update_buttons()
    def update_buttons():
        for control,key in ((primary,"primary"),(secondary,"secondary")):
            action=service_state[key]
            control.set_visible(action is not None)
            if action:
                control.set_label(localized(actions[action]))
            control.set_sensitive(action is not None and not service_busy["value"])
    def refresh_status():
        service_busy["value"]=True
        update_buttons()
        service_info.set_title("Status wird geprüft …" if language=="de" else "Checking status …")
        config=config_entry.get_text().strip()
        def finish(result=None,error=None):
            service_busy["value"]=False
            if error:
                service_state.update(status=None,primary=None,secondary=None)
                service_info.set_title("Prüfung fehlgeschlagen" if language=="de" else "Status check failed")
                service_info.set_subtitle(str(error)[:220])
                update_buttons()
            else:
                display_status(result)
            return False
        def worker():
            try:
                from proton_sync_engine import user_service_lifecycle as lc
                result=lc.status(config,Path(__file__).resolve().parents[2])
                GLib.idle_add(finish,result,None)
            except Exception as exc:
                GLib.idle_add(finish,None,str(exc))
        threading.Thread(target=worker,daemon=True).start()
    def perform(action):
        if service_busy["value"] or action not in (service_state["primary"],service_state["secondary"]):
            return
        service_busy["value"]=True
        update_buttons()
        service_info.set_title("Aktion läuft …" if language=="de" else "Working …")
        def finish(result=None,error=None):
            service_busy["value"]=False
            if error:
                service_state.update(status=None,primary=None,secondary=None)
                service_info.set_title("Aktion fehlgeschlagen" if language=="de" else "Action failed")
                service_info.set_subtitle(str(error)[:220])
                update_buttons()
            else:
                # Confirm the authoritative systemd state after the operation.
                refresh_status()
            return False
        def worker():
            try:
                from proton_sync_engine import user_service_lifecycle as lc
                grants={"install":lc.INSTALL_CONSENT,"enable":lc.ENABLE_CONSENT,
                        "pause":lc.PAUSE_CONSENT,"uninstall":lc.REMOVE_CONSENT}
                result=getattr(lc,action)(config_entry.get_text().strip(),
                              Path(__file__).resolve().parents[2],grants[action])
                GLib.idle_add(finish,result,None)
            except Exception as exc:
                GLib.idle_add(finish,None,str(exc))
        threading.Thread(target=worker,daemon=True).start()
    def ask(action):
        if service_busy["value"] or action not in (service_state["primary"],service_state["secondary"]):
            return
        dialog=Adw.MessageDialog(
            heading=localized(actions[action]),body=localized(descriptions[action]))
        dialog.add_response("cancel","Abbrechen" if language=="de" else "Cancel")
        dialog.add_response("approve","Bestätigen" if language=="de" else "Confirm")
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        if action in ("enable","uninstall"):
            dialog.set_response_appearance("approve",Adw.ResponseAppearance.DESTRUCTIVE)
        def on_response(_dialog,response):
            if response=="approve":
                perform(action)
            else:
                # After cancelling a modal, return keyboard navigation to the
                # action that opened it (only if still visible and enabled).
                def restore():
                    origin=primary if action==service_state["primary"] else secondary
                    if origin.get_visible() and origin.get_sensitive():
                        origin.grab_focus()
                    return False
                GLib.idle_add(restore)
        dialog.connect("response",on_response)
        parent=primary.get_root()
        if isinstance(parent,Gtk.Window):
            dialog.set_transient_for(parent)
        dialog.present()
    primary.connect("clicked",lambda *_: ask(service_state["primary"]))
    secondary.connect("clicked",lambda *_: ask(service_state["secondary"]))
    one_shot=Gtk.Button(label="Einmaligen Testlauf starten" if language=="de" else "Run isolated sync once")
    body.append(one_shot)
    from .run_result_ui import make_result_row, show_result
    result_row=make_result_row(language)
    service_group.add(result_row)
    def on_run_once(*_):
        if (service_busy["value"] or service_state["status"]!="INSTALLED"
            or service_state["primary"]!="enable"):
            return
        dialog=Adw.MessageDialog(
            heading="Einmaliger isolierter Testlauf" if language=="de" else "Single isolated test run",
            body=("Startet nur proton-mvp-isolated-full.service. Der normale Proton-Abgleich bleibt unverändert. "
                  "Es werden ausschließlich neue Testdateien erwartet."
                  if language=="de" else "Starts only the isolated MVP service. Production sync is unchanged."))
        dialog.add_response("cancel","Abbrechen" if language=="de" else "Cancel")
        dialog.add_response("approve","Testlauf starten" if language=="de" else "Start test run")
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        def respond(_dialog,response):
            if response!="approve":return
            from proton_sync_engine.portable_paths import load_paths
            from proton_sync_engine.v1_run_result import baseline_lines, result_after
            try:
                state_dir=load_paths(Path(config_entry.get_text().strip())).state_dir
                start_line=baseline_lines(state_dir)
            except Exception as exc:
                result_row.set_title("Testlauf blockiert")
                result_row.set_subtitle(type(exc).__name__)
                return
            service_busy["value"]=True
            update_buttons()
            one_shot.set_sensitive(False)
            service_info.set_title("Testlauf wird gestartet …" if language=="de" else "Starting isolated test …")
            def finish(error=None):
                service_busy["value"]=False
                if error:
                    service_info.set_title("Testlauf blockiert" if language=="de" else "Test run blocked")
                    service_info.set_subtitle(str(error)[:220])
                    update_buttons()
                else:
                    result_row.set_title("Test läuft · Abschluss wird geprüft" if language=="de" else "Run pending · checking result")
                    def check_result():
                        evidence=result_after(state_dir,start_line)
                        status=evidence['status']
                        return not show_result(result_row,evidence,language)
                    GLib.timeout_add(500,check_result)
                    service_info.set_title("Testlauf angefordert · Ergebnis noch nicht bestätigt"
                                           if language=="de" else "Run requested · outcome not yet verified")
                    update_buttons()
                one_shot.set_sensitive(service_state["status"]=="INSTALLED")
                return False
            def worker():
                try:
                    from proton_sync_engine import user_service_lifecycle as lc
                    lc.run_once(config_entry.get_text().strip(),Path(__file__).resolve().parents[2],lc.RUN_ONCE_CONSENT)
                    GLib.idle_add(finish,None)
                except Exception as exc:
                    GLib.idle_add(finish,str(exc))
            threading.Thread(target=worker,daemon=True).start()
        dialog.connect("response",respond)
        parent=one_shot.get_root()
        if isinstance(parent,Gtk.Window):dialog.set_transient_for(parent)
        dialog.present()
    one_shot.connect("clicked",on_run_once)
    # Only an installed, paused isolated test unit can be started once.
    def refresh_once():
        if not one_shot.get_root():return False
        one_shot.set_visible(service_state["status"]=="INSTALLED"
                             and service_state["primary"]=="enable")
        one_shot.set_sensitive(not service_busy["value"])
        return True
    GLib.timeout_add(150,refresh_once)
    service_note.set_text("Freigabe pro Aktion per Dialog. Die produktiven Sync-Dienste bleiben unverändert."
                          if language=="de" else "Confirm each action in a dialog. Production sync services remain unchanged.")
    update_buttons()
    refresh_status()
    return body
