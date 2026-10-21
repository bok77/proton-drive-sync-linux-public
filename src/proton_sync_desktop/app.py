"""Native GNOME4/libadwaita desktop UI. No user file contents are accessed."""
import gi
gi.require_version("Gtk","4.0")
gi.require_version("Adw","1")
from gi.repository import Adw,Gtk,Gio,GLib,Gdk
from pathlib import Path
import json,locale,sys,threading
from .i18n import translate as tr,validate,event_label,action_text as at,route_edit_text as rt
from . import backend
from .progress import read_progress
from .sync_plan import route_descriptions,unavailable_route_indices
from . import routing
from .setup_wizard import make_page as make_setup_wizard, verified_isolated_pairing

APP_ID="io.github.protondrivesync.Fedora"
LANG=Path.home()/".config/proton-bisync/ui.json"
CSS="""
window { background: @window_bg_color; }
.sync-card { background: @card_bg_color; border: 1px solid alpha(@borders,0.6); border-radius: 15px; padding: 11px; }
.local-card { border-top: 4px solid #3584e4; }
.priority-card { border-top: 4px solid #9141ac; }
.full-card { border-top: 4px solid #26a269; }
.route-index { background: @accent_bg_color; color: @accent_fg_color; border-radius: 30px; min-width: 30px; min-height: 30px; font-weight: 800; }
.route-mapping { background: alpha(@window_bg_color,0.62); border-radius: 10px; padding: 7px; }
.route-arrow { color: @accent_color; font-size: 21px; font-weight: 700; }
.hero { background: alpha(@success_color, 0.12); border: 1px solid alpha(@success_color, 0.28); border-radius: 14px; padding: 13px; }
.hero-offline { background: alpha(@warning_color, 0.12); border-color: alpha(@warning_color, 0.35); }
.monitoring-symbol { color: @success_color; }
.monitoring-symbol-offline { color: @warning_color; }
.metric { background: @card_bg_color; border: 1px solid alpha(@borders, 0.35); border-radius: 12px; padding: 8px; }
.schedule-panel { background: @card_bg_color; border: 1px solid alpha(@borders, 0.38); border-radius: 14px; padding: 15px; }
.schedule-footer { border-top: 1px solid alpha(@borders, 0.3); padding-top: 10px; }
.schedule-choice { min-width: 0; }

.metric-value { font-size: 22px; font-weight: 800; }
.muted { opacity: 0.7; }
.page-heading { font-size: 22px; font-weight: 800; }
.hero-title { font-size: 20px; font-weight: 800; }
.section-label { font-size: 16px; font-weight: 700; }
.status-dot { color: @success_color; }
.warning-dot { color: @warning_color; }
"""
UI_TEXT={
"de":{
"heading":"Automatische Synchronisierung",
"intro":"Lokale Änderungen werden erkannt und hochgeladen. Ausgewählte Cloud-Ordner werden regelmäßig geprüft.",
"local_title":"Linux → Proton Drive",
"priority_title":"Proton Drive → Linux",
"full_title":"Vollständiger Sicherheitsabgleich",
"local_description":"Änderungen im lokalen Ordner werden automatisch erkannt und sicher hochgeladen.",
"priority_description":"Ausgewählte Proton-Ordner werden auf Änderungen geprüft und lokal aktualisiert.",
"full_description":"Regelmäßige Kontrolle aller Ordner – auch für Cloud-Änderungen, die die lokale Überwachung nicht sieht.",
"source":"QUELLE","destination":"ZIEL","cadence":"Prüfung alle {minutes} Minuten",
"watcher_addition":" · zusätzlich bei lokalen Änderungen",
"upload_now":"Jetzt hochladen","check_now":"Jetzt prüfen",
"full_now":"Jetzt abgleichen","edit":"⚙  Einstellungen",
"summary":"Synchronisationsstatus","running":"Abgleich läuft …",
"monitoring":"Automatische Erkennung lokaler Änderungen aktiv", "monitoring_off":"Dateiüberwachung gestoppt",
"watcher_explanation":"Änderungen in lokalen Linux-Ordnern werden erkannt. Der Cloud-Abgleich läuft unabhängig davon.",
"watcher_warning":"Änderungen werden derzeit nicht automatisch erkannt. Der regelmäßige Abgleich bleibt verfügbar.",
"all_good":"Sync-Dienste bereit",
"full_note":"Auch nach dem ersten Abgleich regelmäßig notwendig, da Änderungen in Proton sonst unentdeckt bleiben.",
"watcher_switch":"Dateiüberwachung", "watcher_on":"Ein", "watcher_off":"Aus",
"watcher_disabled":"Dateiüberwachung ausgeschaltet",
"watcher_disabled_description":"Automatische Erkennung ist aus. Der 5-Minuten-Abgleich läuft weiterhin.",
"watcher_change_failed":"Dateiüberwachung konnte nicht umgestellt werden",
"monitoring_both":"Synchronisationsüberwachung",
"local_active":"Linux: Änderungserkennung läuft",
"local_inactive":"Linux: Änderungserkennung deaktiviert",
"local_error":"Linux: Überwachung ausgefallen",
"cloud_active":"Proton Drive: regelmäßige Cloud-Prüfung aktiv",
"cloud_partial":"Proton Drive: Cloud-Prüfung teilweise aktiv",
"cloud_inactive":"Proton Drive: Cloud-Prüfung gestoppt",
"cloud_last":"Letzte erfolgreiche Cloud-Prüfung: {when}",
"cloud_no_success":"Noch kein erfolgreicher Cloud-Abgleich nachgewiesen",
"local_switch_only":"Lokale Überwachung einstellen",
"full_healthy":"Vollständiger Abgleich aktiv",
"full_success":"Letzter erfolgreicher Vollabgleich: {when} · alle {minutes} Minuten",
"full_warning":"Vollständiger Abgleich benötigt Aufmerksamkeit",
"full_unknown":"Noch kein erfolgreich abgeschlossener Vollabgleich",
"switch_off":"Lokale Überwachung ausschalten",
"switch_on":"Lokale Überwachung einschalten",
"measured":"{done} von {total} Dateien geprüft · {pct}%", "cloud_inventory":"Cloud-Ordner werden erfasst …",
"new_files":"Neue lokale Dateien werden geprüft …", "remaining_changes":"Weitere Änderungen werden abgeglichen …",
"unknown":"Abgleich läuft …", "tracked_files":"Bekannte Dateien werden geprüft",
"file_comparison":"Cloud-Dateien werden geprüft",
},
"en":{
"heading":"Automatic synchronization",
"intro":"Local changes are detected and uploaded. Selected cloud folders are checked regularly.",
"local_title":"Linux → Proton Drive",
"priority_title":"Proton Drive → Linux",
"full_title":"Full integrity scan",
"local_description":"Local folder changes are detected automatically and uploaded safely.",
"priority_description":"Selected Proton folders are checked and local copies updated.",
"full_description":"Regularly check every folder, including remote changes invisible to local file monitoring.",
"source":"SOURCE","destination":"DESTINATION","cadence":"Scan every {minutes} minutes",
"watcher_addition":" · also on local changes",
"upload_now":"Upload now","check_now":"Check now",
"full_now":"Sync now","edit":"⚙  Settings",
"summary":"Sync status","running":"Sync in progress …",
"monitoring":"Automatic local change detection is active", "monitoring_off":"File monitoring stopped",
"watcher_explanation":"Changes in local Linux folders are detected. Cloud scanning works independently.",
"watcher_warning":"Changes are not detected automatically right now. Scheduled sync remains available.",
"all_good":"Sync services ready",
"full_note":"Still required after initial setup because changes elsewhere in Proton may otherwise go unnoticed.",
"watcher_switch":"File monitoring", "watcher_on":"On", "watcher_off":"Off",
"watcher_disabled":"File monitoring turned off",
"watcher_disabled_description":"Automatic detection is off. The scheduled five-minute sync continues.",
"watcher_change_failed":"Could not change file monitoring",
"monitoring_both":"Synchronization monitoring",
"local_active":"Linux: change detection running",
"local_inactive":"Linux: change detection disabled",
"local_error":"Linux: change detection unavailable",
"cloud_active":"Proton Drive: scheduled cloud checks active",
"cloud_partial":"Proton Drive: cloud checks partially active",
"cloud_inactive":"Proton Drive: cloud checks stopped",
"cloud_last":"Last successful cloud check: {when}",
"cloud_no_success":"No successful cloud check confirmed yet",
"local_switch_only":"Configure local monitoring",
"full_healthy":"Full reconciliation active",
"full_success":"Last successful full scan: {when} · every {minutes} minutes",
"full_warning":"Full scan needs attention",
"full_unknown":"No successful full reconciliation yet",
"switch_off":"Turn off local monitoring",
"switch_on":"Turn on local monitoring",
"measured":"{done} of {total} files checked · {pct}%", "cloud_inventory":"Reading cloud folders …",
"new_files":"Checking new local files …", "remaining_changes":"Reconciling remaining changes …",
"unknown":"Sync in progress …", "tracked_files":"Checking known files",
"file_comparison":"Checking cloud files",
},
}
DASHBOARD_TEXT={
"de":{
"headline":"Meine Dateien sind synchronisiert",
"attention":"Synchronisierung prüfen",
"running_headline":"Synchronisierung läuft",
"local":"Linux – lokale Änderungen",
"cloud":"Proton Drive – Cloud-Änderungen",
"local_on":"Automatische Erkennung eingeschaltet",
"local_off":"Automatische Erkennung ausgeschaltet",
"cloud_on":"Regelmäßige Cloud-Prüfung eingeschaltet",
"cloud_off":"Cloud-Prüfung nicht vollständig aktiv",
"toggle":"Lokale Erkennung aktivieren",
"main_button":"Jetzt synchronisieren",
"main_explain":"Prüft beide Seiten und übernimmt notwendige Änderungen.",
"advanced":"Erweiterte Einstellungen und Einzelprüfungen",
"local_direction":"Lokaler Ordner → Proton Drive",
"cloud_direction":"Proton Drive → lokaler Ordner",
"fallback":"Zusätzliche Sicherheitsprüfung alle {minutes} Minuten",
"cloud_cadence":"Bevorzugte Cloud-Ordner alle {minutes} Minuten",
"background":"Vollständige Kontrolle alle {minutes} Minuten",
"last_full":"Letzter erfolgreicher Abgleich: {time}",
"next_full":"Nächster geplanter Abgleich: {time}",
"next_disabled":"Nächster Abgleich: nicht geplant (Cloud-Überwachung aus)",
"next_unknown":"Nächster Abgleich: derzeit kein Zeitplan verfügbar",
"currently_running":"Vollständiger Abgleich läuft gerade …",
"status_unknown":"Noch kein erfolgreicher vollständiger Abgleich nachgewiesen",
"email_gate":"Nach dem öffentlichen Release: Link per E-Mail senden",
"schedule_heading":"Automatische Prüfintervalle",
"local_schedule":"Linux-Prüfung",
"priority_schedule":"Cloud-Ordner",
"full_schedule":"Gesamtabgleich",
"watcher_hint":"Lokale Änderungen werden zusätzlich sofort erkannt.",
"schedule_save":"Intervalle speichern",
"schedule_saved":"Gespeichert",
"schedule_busy":"Wird übernommen …",
"schedule_ready":"Änderungen werden automatisch übernommen",
"schedule_failed":"Zeitplan konnte nicht übernommen werden",
"preview_section":"Erst sehen, dann entscheiden",
"minutes":"{minutes} Min.",
"preview":"Änderungen vorab prüfen",
"preview_explain":"Zeigt vorab, welche Dateien hoch- oder heruntergeladen würden. Es wird nichts verändert.",
"preview_wait":"Cloud und Linux werden gelesen – das kann länger dauern …",
"preview_title":"Änderungen vorab prüfen",
"preview_limits":"Beide Seiten wurden gelesen. Nur eine Momentaufnahme: Vor jeder Ausführung werden Dateistände und Cloud-Versionen erneut geprüft. Keine Änderung wurde ausgeführt.",
"preview_summary":"Neue Dateien: {new} · Mögliche Löschungen: {delete} · Umbenennungen: {rename}",
"preview_empty":"Keine lokalen Änderungen gefunden",
"cloud_failed":"Cloud-Überwachung konnte nicht umgestellt werden",
"preview_counts":"Hochladen: {upload} · Herunterladen: {download} · Konflikte: {conflict} · Löschkandidaten: {deletions}",
},
"en":{
"headline":"Your files are synchronized",
"attention":"Sync needs attention",
"running_headline":"Synchronization in progress",
"local":"Linux – local changes",
"cloud":"Proton Drive – cloud changes",
"local_on":"Automatic change detection enabled",
"local_off":"Automatic change detection disabled",
"cloud_on":"Scheduled cloud checks enabled",
"cloud_off":"Cloud checks not fully active",
"toggle":"Enable local change detection",
"main_button":"Sync now",
"main_explain":"Checks both sides and applies necessary changes.",
"advanced":"Advanced settings and individual checks",
"local_direction":"Local folder → Proton Drive",
"cloud_direction":"Proton Drive → local folder",
"fallback":"Additional fallback scan every {minutes} minutes",
"cloud_cadence":"Priority cloud folders every {minutes} minutes",
"background":"Full consistency scan every {minutes} minutes",
"last_full":"Last successful sync: {time}",
"next_full":"Next scheduled sync: {time}",
"next_disabled":"Next sync: not scheduled (cloud monitoring off)",
"next_unknown":"Next sync: schedule currently unavailable",
"currently_running":"Full synchronization is currently running …",
"status_unknown":"No successful full reconciliation confirmed yet",
"email_gate":"After public release: email the release link",
"schedule_heading":"Automatic check intervals",
"local_schedule":"Linux check",
"priority_schedule":"Cloud folders",
"full_schedule":"Full scan",
"watcher_hint":"Local file changes are also detected immediately.",
"schedule_save":"Save intervals",
"schedule_saved":"Saved",
"schedule_busy":"Applying …",
"schedule_ready":"Changes are applied automatically",
"schedule_failed":"Could not update schedule",
"preview_section":"Review before deciding",
"minutes":"{minutes} min",
"preview":"Preview changes first",
"preview_explain":"See proposed uploads and downloads without modifying any files.",
"preview_wait":"Reading cloud and Linux – this may take a while …",
"preview_title":"Preview changes first",
"preview_limits":"Both sides were read. This is only a snapshot; all local and cloud versions must be revalidated before applying changes. No changes were made.",
"preview_summary":"New files: {new} · Possible deletions: {delete} · Renames: {rename}",
"preview_empty":"No local changes found",
"cloud_failed":"Could not change cloud monitoring",
"preview_counts":"Uploads: {upload} · Downloads: {download} · Conflicts: {conflict} · Deletion candidates: {deletions}",
}}
def preferred():
    """Resolve saved or system locale without requiring a network lookup."""
    try:
        saved=json.loads(LANG.read_text()).get("language","system")
        if saved in ("de","en"):return saved
    except (OSError,ValueError):pass
    code=(locale.getlocale()[0] or "").lower()
    return "de" if code.startswith("de") else "en"

def save_language(lang):
    """Persist the preferred interface language in the user configuration."""
    LANG.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    LANG.write_text(json.dumps({"language":lang}))

def label(text,css=None,wrap=False):
    """Create a GTK label with consistent alignment and optional style."""
    obj=Gtk.Label(label=text,xalign=0)
    obj.set_wrap(wrap)
    if css:obj.add_css_class(css)
    return obj

def stack_box(horizontal=False,spacing=12):
    """Return a GTK box used by the compact responsive layouts."""
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL if horizontal else Gtk.Orientation.VERTICAL,spacing=spacing)

class Window(Adw.ApplicationWindow):
    def __init__(self,app):
        """Build the local application window and register periodic status refreshes."""
        super().__init__(application=app,title=tr(app.language,"app"))
        self.app=app
        self.set_default_size(1180,750)
        self.set_size_request(530,490)
        view=Adw.ToolbarView()
        header=Adw.HeaderBar()
        self.title_widget=Adw.WindowTitle(title=tr(app.language,"app"),subtitle=tr(app.language,"development"))
        header.set_title_widget(self.title_widget)
        refresh=Gtk.Button(icon_name="view-refresh-symbolic",tooltip_text=tr(app.language,"refresh"))
        refresh.connect("clicked",lambda *_:self.refresh())
        header.pack_end(refresh)
        view.add_top_bar(header)
        self.tabs=Adw.ViewStack()
        self.pages={}
        if getattr(app,"public_alpha",False):
            self.pages["overview"]=self.tabs.add_titled(self.scroll_page(self.make_public_alpha_info()),"overview",tr(app.language,"overview"))
            self.pages["settings"]=self.tabs.add_titled(self.scroll_page(self.make_public_alpha_settings()),"settings",tr(app.language,"settings"))
        else:
            self.pages["overview"]=self.tabs.add_titled(self.scroll_page(self.make_overview()),"overview",tr(app.language,"overview"))
            self.pages["activity"]=self.tabs.add_titled(self.scroll_page(self.make_activity()),"activity",tr(app.language,"activity"))
            self.pages["settings"]=self.tabs.add_titled(self.scroll_page(self.make_settings()),"settings",tr(app.language,"settings"))
        # The setup wizard is a one-time onboarding screen, not a permanent tab.
        # All overview, activity and settings controls remain unchanged.
            if not verified_isolated_pairing():
                self.pages["setup"]=self.tabs.add_titled(self.scroll_page(make_setup_wizard(app.language)),"setup","Einrichtung" if app.language=="de" else "Setup")
        switch=Adw.ViewSwitcherBar(stack=self.tabs)
        switch.set_reveal(True)
        layout=stack_box(spacing=0)
        layout.append(self.tabs)
        self.tabs.set_vexpand(True)
        layout.append(switch)
        view.set_content(layout)
        self.set_content(view)
        self.refresh()
        GLib.timeout_add_seconds(20,self.refresh)
    def make_public_alpha_info(self):
        """Show a safe preview without any production sync or cloud mutation controls."""
        outer=stack_box(spacing=15)
        for side in ("top","bottom","start","end"):
            getattr(outer,"set_margin_"+side)(22)
        outer.append(label("Proton Drive Sync · Experimental Alpha", "page-heading"))
        outer.append(label("Public-alpha preview only: synchronization is disabled until a separate portable installation and safety review are approved.", "muted",True))
        outer.append(label("No existing systemd services are modified. Do not use personal files.", "muted",True))
        from proton_sync_engine.alpha_profile import public_alpha_profile_status
        profile_status=public_alpha_profile_status()
        outer.append(label("Isolated profile: " + ("configured but inactive" if profile_status=="CONFIGURED_NOT_ACTIVATED" else "not configured"), "muted",True))
        from .run_result_ui import make_result_row
        self.alpha_result=make_result_row(self.app.language)
        group=Adw.PreferencesGroup()
        group.add(self.alpha_result)
        outer.append(group)
        for action,caption in (("install","Install isolated test service"),
                               ("start_once","Run isolated test once"),
                               ("remove","Remove isolated test service")):
            button=Gtk.Button(label=caption)
            button.connect("clicked",lambda _button,operation=action:self.alpha_confirm(operation))
            button.set_sensitive(profile_status=="CONFIGURED_NOT_ACTIVATED")
            outer.append(button)
        return outer

    def alpha_confirm(self,operation):
        """Request explicit approval for the existing isolated lifecycle only."""
        from proton_sync_engine import alpha_lifecycle
        from proton_sync_engine import user_service_lifecycle as lc
        grants={"install":lc.INSTALL_CONSENT,"start_once":lc.RUN_ONCE_CONSENT,
                "remove":lc.REMOVE_CONSENT}
        if operation not in grants:return
        bundle=Path(__file__).resolve().parents[2]
        dialog=Adw.AlertDialog(heading="Isolated alpha test: " + operation,
                               body="Uses only a private, verified alpha profile and isolated systemd units. No production services will be modified.")
        dialog.add_response("cancel","Cancel")
        dialog.add_response("approve","Confirm")
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        def respond(_dialog,response):
            if response!="approve":return
            from proton_sync_engine.alpha_profile import load_alpha_profile
            from proton_sync_engine.v1_run_result import baseline_lines,result_after
            try:
                state_dir=load_alpha_profile().paths.state_dir
                marker=baseline_lines(state_dir) if operation=="start_once" else None
            except Exception as exc:
                self.dialog("Alpha action blocked",type(exc).__name__)
                return
            def work():
                try:
                    getattr(alpha_lifecycle,operation)(bundle,consent=grants[operation])
                    GLib.idle_add(finish,None)
                except Exception as exc:
                    GLib.idle_add(finish,type(exc).__name__)
            def finish(error):
                if error:
                    self.dialog("Alpha action blocked",error)
                elif operation=="start_once":
                    from .run_result_ui import show_result
                    show_result(self.alpha_result,{'status':'PENDING'},self.app.language)
                    from time import monotonic
                    deadline=monotonic()+660
                    def check():
                        evidence=result_after(state_dir,marker)
                        if evidence['status']=='PENDING' and monotonic()>=deadline:
                            evidence={'status':'UNKNOWN'}
                        return not show_result(self.alpha_result,evidence,self.app.language)
                    GLib.timeout_add(500,check)
                else:
                    self.dialog("Isolated alpha", "Request completed. Restart the preview to refresh available actions.")
                return False
            threading.Thread(target=work,daemon=True).start()
        dialog.connect("response",respond)
        dialog.present(self)

    def make_public_alpha_settings(self):
        """Expose informational settings without developer-specific systemd controls."""
        outer=stack_box(spacing=15)
        for side in ("top","bottom","start","end"):
            getattr(outer,"set_margin_"+side)(22)
        outer.append(label("Alpha safety settings", "page-heading"))
        outer.append(label("This preview deliberately does not configure cloud credentials, timers, production routes, or personal file paths.","muted",True))
        return outer

    def t(self,key):
        """Translate a standard interface caption into the selected language."""
        return tr(self.app.language,key)
    def a(self,key):
        """Translate guided synchronization actions and schedule descriptions."""
        return at(self.app.language,key)
    def e(self,key):
        """Translate route configuration and validation controls."""
        return rt(self.app.language,key)
    def scroll_page(self,child):
        """Wrap a page in a narrow-window-friendly scroll container."""
        scroll=Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        clamp=Adw.Clamp(maximum_size=1350,tightening_threshold=1100)
        clamp.set_child(child)
        scroll.set_child(clamp)
        return scroll
    def d(self,key):
        """Return task-first, bilingual dashboard copy."""
        return DASHBOARD_TEXT["de" if self.app.language=="de" else "en"][key]

    def make_overview(self):
        """Build one consumer-facing sync task with directly accessible controls.

        Local and cloud detection are separate observable rows, but users see a
        single synchronizing action. Technical per-direction starts remain under
        the advanced disclosure.
        """
        outer=stack_box(spacing=14)
        for side in ("top","bottom","start","end"):
            getattr(outer,"set_margin_"+side)(18)
        hero=stack_box(spacing=7);hero.add_css_class("hero")
        title_line=stack_box(horizontal=True,spacing=10)
        self.monitor_icon=Gtk.Image.new_from_icon_name("emblem-ok-symbolic")
        self.monitor_icon.set_pixel_size(28)
        title_line.append(self.monitor_icon)
        header=stack_box(spacing=3);header.set_hexpand(True)
        self.hero_title=label(self.d("headline"),"hero-title")
        self.full_health_detail=label("", "muted",True)
        self.next_full_detail=label("", "muted",True)
        header.append(self.hero_title)
        header.append(self.full_health_detail)
        header.append(self.next_full_detail)
        title_line.append(header);hero.append(title_line)
        self.monitor_health=label("", "muted",True);hero.append(self.monitor_health)
        self.monitor_hero=hero;outer.append(hero)
        # Prominent, factual running state directly beneath the health card.
        self.progressbar=Gtk.ProgressBar()
        self.progressbar.set_visible(False)
        outer.append(self.progressbar)
        self.progress_spinner=Gtk.Spinner()
        self.progress_spinner.set_visible(False)
        outer.append(self.progress_spinner)
        self.progress_note=label("", "muted",True)
        self.progress_note.set_visible(False)
        outer.append(self.progress_note)
        overview=Adw.PreferencesGroup()
        local=Adw.ActionRow(title=self.d("local"),subtitle=self.d("local_on"))
        self.local_status=local
        self.monitor_switch=Gtk.Switch()
        self.monitor_switch.set_valign(Gtk.Align.CENTER)
        self.monitor_switch.connect("state-set",self.change_watcher_status)
        local.add_suffix(self.monitor_switch)
        overview.add(local)
        cloud=Adw.ActionRow(title=self.d("cloud"),subtitle=self.d("cloud_on"))
        self.cloud_status=cloud
        self.cloud_switch=Gtk.Switch()
        self.cloud_switch.set_valign(Gtk.Align.CENTER)
        self.cloud_switch.connect("state-set",self.change_cloud_status)
        cloud.add_suffix(self.cloud_switch)
        overview.add(cloud)
        outer.append(overview)
        # Selecting a supported cadence saves immediately in a background worker.
        # Failed updates are reverted after a verified systemd readback.
        scheduler=stack_box(spacing=11)
        scheduler.add_css_class("schedule-panel")
        self.scheduler_heading=label(self.d("schedule_heading"),"section-label")
        scheduler.append(self.scheduler_heading)
        choices=Gtk.Grid(column_spacing=13,row_spacing=8)
        choices.set_column_homogeneous(True)
        choices.set_hexpand(True)
        self.cadence_controls={}
        self._updating_intervals=True
        self._saving_intervals=False
        self._interval_pending=None
        current=routing.load()["interval_minutes"]
        for index,kind in enumerate(("local","priority","full")):
            section=stack_box(spacing=6)
            section.add_css_class("schedule-choice")
            section.set_hexpand(True)
            heading=label(self.d(("local_schedule","priority_schedule","full_schedule")[index]),
                          "muted",True)
            section.append(heading)
            allowed=routing.SUPPORTED[kind]
            selector=Gtk.DropDown.new_from_strings(
                [self.d("minutes").format(minutes=value) for value in allowed])
            selector.set_hexpand(True)
            selector.set_selected(allowed.index(current[kind]))
            section.append(selector)
            choices.attach(section,index,0,1,1)
            self.cadence_controls[kind]=selector
            selector.connect("notify::selected",self.interval_changed,kind)
        self._updating_intervals=False
        scheduler.append(choices)
        footer=stack_box(horizontal=True,spacing=12)
        footer.add_css_class("schedule-footer")
        footer.set_hexpand(True)
        explanation=label(self.d("watcher_hint"),"muted",True)
        explanation.set_hexpand(True)
        explanation.set_valign(Gtk.Align.CENTER)
        footer.append(explanation)
        self.interval_feedback=label(self.d("schedule_ready"),"muted",True)
        self.interval_feedback.set_valign(Gtk.Align.CENTER)
        footer.append(self.interval_feedback)
        scheduler.append(footer)
        outer.append(scheduler)
        action=stack_box(spacing=7)
        self.main_sync=Gtk.Button(label=self.d("main_button"))
        self.main_sync.add_css_class("suggested-action")
        self.main_sync.set_size_request(-1,52)
        self.main_sync.connect("clicked",lambda *_:self.start_route(2))
        action.append(self.main_sync)
        action.append(label(self.d("main_explain"),"muted",True))
        preview_row=Adw.ActionRow(title=self.d("preview_section"),
                                  subtitle=self.d("preview_explain"))
        self.preview_button=Gtk.Button(label=self.d("preview"))
        self.preview_button.add_css_class("flat")
        self.preview_button.set_valign(Gtk.Align.CENTER)
        self.preview_button.connect("clicked",self.preview_changes)
        preview_row.add_suffix(self.preview_button)
        preview_group=Adw.PreferencesGroup()
        preview_group.add(preview_row)
        action.append(preview_group)
        outer.append(action)
        self.routes_heading=label(self.d("advanced"),"section-label")
        self.details_expander=Gtk.Expander(label=self.d("advanced"))
        details=stack_box(spacing=10)
        self.route_widgets=[]
        for index in range(3):
            line=Adw.PreferencesGroup()
            labels=(self.d("local_direction"),self.d("cloud_direction"),self.u("full_title"))
            row=Adw.ActionRow(title=labels[index],subtitle="…")
            start=Gtk.Button(label=self.u(("upload_now","check_now","full_now")[index]))
            start.connect("clicked",lambda button,i=index:self.start_route(i))
            row.add_suffix(start)
            edit=Gtk.Button(label=self.u("edit"))
            edit.connect("clicked",lambda button,i=index:self.edit_route(i))
            row.add_suffix(edit)
            line.add(row);details.append(line)
            self.route_widgets.append(dict(
                source=Gtk.Label(),destination=Gtk.Label(),cadence=row,
                progress=Gtk.ProgressBar(),running=Gtk.Label(),action=start))
        self.details_expander.set_child(details);outer.append(self.details_expander)
        self.progress_title=label(self.u("summary"),"section-label")
        outer.append(self.progress_title)
        metrics=stack_box(horizontal=True,spacing=10);metrics.set_homogeneous(True)
        self.metric_widgets={}
        for key in ("tracked","waiting","conflicts"):
            card=stack_box(spacing=2);card.add_css_class("metric")
            name=label(self.t(key),"muted")
            value=label("—","metric-value")
            card.append(name);card.append(value);metrics.append(card)
            self.metric_widgets[key]=(name,value)
        outer.append(metrics)
        self.local_row=Adw.ActionRow(title=self.t("last_local"),subtitle=self.t("unknown"))
        self.cloud_row=Adw.ActionRow(title=self.t("cloud_priority"),subtitle=self.t("unknown"))
        self.full_row=Adw.ActionRow(title=self.t("last_cloud"),subtitle=self.t("unknown"))
        self.service_rows={}
        for key in ("watcher","local_timer","cloud_timer","full_timer","health_timer"):
            self.service_rows[key]=(Adw.ActionRow(title=self.t(key)),Gtk.Label())
        GLib.timeout_add_seconds(3,self.update_running)
        return outer

    def interval_changed(self,selector,property_spec,kind):
        """Persist a user-selected interval automatically, without a Save button.

        Coalesce further selections during a write; do not block the GTK thread.
        Programmatic changes and initial selector setup are never persisted.
        """
        if getattr(self,"_updating_intervals",False):
            return
        options=routing.SUPPORTED[kind]
        index=selector.get_selected()
        if index>=len(options):
            return
        self._interval_pending=(kind,options[index])
        if not self._saving_intervals:
            self._apply_pending_interval()

    def _apply_pending_interval(self):
        """Start the latest requested change with a single in-flight worker."""
        if self._interval_pending is None:
            self._saving_intervals=False
            self.interval_feedback.set_text(self.d("schedule_saved"))
            return False
        kind,minutes=self._interval_pending
        self._interval_pending=None
        self._saving_intervals=True
        self.interval_feedback.set_text(self.d("schedule_busy"))
        def worker():
            error=None
            try:
                original=routing.load()
                if not backend.cloud_monitor_enabled():
                    raise RuntimeError(self.d("cloud_off"))
                proposed={**original,"interval_minutes":dict(original["interval_minutes"])}
                proposed["interval_minutes"][kind]=minutes
                if proposed!=original:
                    applied=routing.apply(proposed)
                    if applied["interval_minutes"]!=proposed["interval_minutes"]:
                        raise RuntimeError("Interval readback mismatch")
            except Exception as exc:
                error=str(exc)
            GLib.idle_add(self._interval_write_finished,kind,minutes,error)
        threading.Thread(target=worker,daemon=True).start()
        return False

    def _interval_write_finished(self,kind,minutes,error):
        """Read back the applied values; revert failed selections without looping."""
        try:
            actual=routing.load()["interval_minutes"]
        except Exception as exc:
            error=error or str(exc)
            actual=None
        if actual is not None:
            self._updating_intervals=True
            try:
                for name,selector in self.cadence_controls.items():
                    pending=self._interval_pending
                    if pending is not None and pending[0]==name:
                        continue
                    selector.set_selected(routing.SUPPORTED[name].index(actual[name]))
            finally:
                self._updating_intervals=False
        if error:
            self.interval_feedback.set_text(self.d("schedule_failed"))
            self.dialog(self.d("schedule_failed"),error)
        else:
            self.interval_feedback.set_text(self.d("schedule_saved"))
            self.refresh()
        if self._interval_pending is not None:
            self._apply_pending_interval()
        else:
            self._saving_intervals=False
        return False

    def change_cloud_status(self,switch,requested):
        """Control both scheduled cloud monitors, never the local watcher.

        A failed update restores the actual systemd state in the dashboard.
        The manual full reconciliation remains available even while disabled.
        """
        if getattr(self,"_updating_cloud_switch",False):
            return True
        try:
            backend.set_cloud_monitor_enabled(bool(requested))
        except Exception as exc:
            self.dialog(self.d("cloud_failed"),str(exc))
        self.refresh()
        return True

    def preview_changes(self,*_):
        """Run the read-only bidirectional preview off the GTK main thread."""
        self.preview_button.set_sensitive(False)
        self.preview_button.set_label(self.d("preview_wait"))
        def task():
            try:
                result=backend.create_change_preview()
                error=None
            except Exception as exc:
                result=None
                error=str(exc)
            GLib.idle_add(self.show_change_preview,result,error)
        threading.Thread(target=task,daemon=True).start()

    def show_change_preview(self,result,error):
        """Show all proposed operations in a scrollable, read-only review window."""
        self.preview_button.set_sensitive(True)
        self.preview_button.set_label(self.d("preview"))
        if error:
            self.dialog(self.t("error"),error)
            return False
        counts=result["counts"]
        deletions=sum(counts.get(key,0) for key in (
            "pending_deletion","pending_local_deletion","pending_cloud_deletion"))
        summary=self.d("preview_counts").format(
            upload=counts.get("upload",0),
            download=counts.get("download",0),
            conflict=counts.get("conflict",0),
            deletions=deletions)
        window=Gtk.Window(title=self.d("preview_title"),transient_for=self,modal=True)
        window.set_default_size(800,600)
        container=stack_box(spacing=12)
        for side in ("top","bottom","start","end"):
            getattr(container,"set_margin_"+side)(16)
        container.append(label(summary,"section-label",True))
        container.append(label(self.d("preview_limits"),"muted",True))
        content=Gtk.TextView()
        content.set_editable(False)
        content.set_cursor_visible(False)
        content.set_monospace(True)
        content.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        lines=[]
        for item in result["changes"]:
            lines.append(str(item["action"])+"  |  "+str(item["reason"])+"  |  "+str(item["path"]))
        content.get_buffer().set_text("\n".join(lines) if lines else self.d("preview_empty"))
        scroller=Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        scroller.set_child(content)
        scroller.set_vexpand(True)
        container.append(scroller)
        close=Gtk.Button(label=self.t("close"))
        close.connect("clicked",lambda *_:window.close())
        container.append(close)
        window.set_child(container)
        window.present()
        return False

    def toggle_monitoring(self,*_):
        """Toggle only the local watcher, preserving scheduled cloud scans."""
        try:
            requested=not backend.watcher_enabled()
            backend.set_watcher_enabled(requested)
        except Exception as exc:
            self.dialog(self.u("watcher_change_failed"),str(exc))
        self.refresh()

    def change_watcher_status(self,switch,requested):
        """Persist the explicit monitoring choice, verifying the systemd readback.

        On a failed change, the visual switch reverts to the verified state.
        This never stops the five-minute fallback or the cloud timers.
        """
        if getattr(self,"_updating_monitor_switch",False):
            return True
        try:
            backend.set_watcher_enabled(bool(requested))
        except Exception as exc:
            self.dialog(self.u("watcher_change_failed"),str(exc))
        self.refresh()
        return True

    def update_running(self):
        """Expose actual full-scan progress, never synthetic percentages."""
        active=backend.service_active("proton-bisync.service")
        quick=backend.service_active("proton-bisync-quick.service")
        priority=backend.service_active("proton-cloud-priority.service")
        from .progress import read_progress
        model=read_progress(backend.STATE,"full",active)
        if model["mode"]=="measured":
            self.progress_spinner.stop()
            self.progress_spinner.set_visible(False)
            self.progressbar.set_visible(True)
            self.progressbar.set_fraction(model["fraction"])
            self.progress_note.set_visible(True)
            self.progress_note.set_text(self.u("measured").format(
                done=model["done"],total=model["total"],
                pct=round(model["fraction"]*100)))
        elif model["mode"]=="working":
            self.progressbar.set_visible(False)
            self.progress_spinner.set_visible(True)
            self.progress_spinner.start()
            self.progress_note.set_visible(True)
            self.progress_note.set_text(self.u(model.get("phase","unknown")))
        elif quick or priority:
            self.progressbar.set_visible(False)
            self.progress_spinner.set_visible(True)
            self.progress_spinner.start()
            self.progress_note.set_visible(True)
            self.progress_note.set_text(
                "Schnellabgleich läuft …" if quick and self.app.language=="de" else
                "Cloud-Prüfung läuft …" if priority and self.app.language=="de" else
                "Quick synchronization running …" if quick else "Cloud check running …")
        else:
            self.progress_spinner.stop()
            self.progress_spinner.set_visible(False)
            self.progressbar.set_visible(False)
            self.progress_note.set_visible(False)
        return True

    def u(self,key):
        """Translate every prominent card title, action, and activity label."""
        return UI_TEXT["de" if self.app.language=="de" else "en"][key]

    def start_route(self,index):
        """Request the existing guarded systemd service for the chosen route."""
        callbacks=(backend.request_local_sync,backend.request_priority_sync,
                   backend.request_full_sync)
        self._request_sync(callbacks[index])
        self.update_running()

    def edit_route(self,index):
        """Edit one actual sync route and show a folder chooser where supported.

        The root mapping is displayed, not silently migrated. The priority
        route can edit its cloud subfolders. All routes can change their timer
        cadence; changes are applied only after validation and readback.
        """
        config=routing.load()
        kinds=("local","priority","full")
        kind=kinds[index]
        dialog=Adw.AlertDialog(heading=self.e("route_settings"),body="")
        dialog.add_response("cancel",self.t("close"))
        dialog.add_response("save",self.e("save_routes"))
        dialog.set_response_appearance("save",Adw.ResponseAppearance.SUGGESTED)
        box=stack_box(spacing=12)
        box.set_margin_top(7)
        # This is an explicit, editable mapping only for the priority folders.
        local_row=Adw.EntryRow(title=self.e("local_folder"))
        local_row.set_text(str(routing.ROOT))
        local_row.set_editable(False)
        box.append(local_row)
        choose=Gtk.Button(label=self.e("browse"))
        choose.connect("clicked",self.choose_folder,local_row)
        box.append(choose)
        hint=label(self.e("root_locked"),"muted",True)
        box.append(hint)
        cloud=Adw.EntryRow(title=self.e("cloud_folder"))
        cloud.set_text("/my-files")
        cloud.set_editable(False)
        box.append(cloud)
        priority_field=None
        if kind=="priority":
            box.append(label(self.e("choose_priority"),"section-label"))
            priority_field=Gtk.TextView()
            priority_field.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            priority_field.set_size_request(450,85)
            priority_field.get_buffer().set_text("\n".join(config["priority_cloud_folders"]))
            scroller=Gtk.ScrolledWindow()
            scroller.set_min_content_height(90)
            scroller.set_child(priority_field)
            box.append(scroller)
            box.append(label(self.e("priority_hint"),"muted",True))
            browse_cloud=Gtk.Button(label=self.e("browse"))
            browse_cloud.connect("clicked",lambda *_:self.browse_cloud_folder(priority_field))
            box.append(browse_cloud)
        box.append(label(self.e("frequency"),"section-label"))
        options=routing.SUPPORTED[kind]
        chooser=Gtk.DropDown.new_from_strings([str(n)+" min" for n in options])
        chooser.set_selected(options.index(config["interval_minutes"][kind]))
        box.append(chooser)
        dialog.set_extra_child(box)
        def submitted(d,response):
            if response!="save":return
            try:
                proposed=routing.load()
                proposed["interval_minutes"][kind]=options[chooser.get_selected()]
                if priority_field is not None:
                    buf=priority_field.get_buffer()
                    text=buf.get_text(buf.get_start_iter(),buf.get_end_iter(),False)
                    proposed["priority_cloud_folders"]=[line.strip() for line in text.splitlines() if line.strip()]
                if priority_field is not None:
                    backend.verify_cloud_directories(proposed["priority_cloud_folders"])
                routing.apply(proposed)
                self.refresh()
                self.dialog(self.t("success"),self.e("configured"))
            except Exception as exc:
                self.dialog(self.e("config_failed"),str(exc))
        dialog.connect("response",submitted)
        dialog.present(self)

    def browse_cloud_folder(self,priority_field):
        """Navigate verified Proton cloud folders and append a selected subfolder.

        The browser is read-only; typing paths manually remains an alternative.
        """
        dialog=Adw.AlertDialog(heading=self.e("select_folder"),body="/my-files")
        dialog.add_response("close",self.t("close"))
        content=stack_box(spacing=8)
        current={"path":"/my-files"}
        heading=label("/my-files","muted",True)
        content.append(heading)
        scroll=Gtk.ScrolledWindow()
        scroll.set_min_content_height(210)
        scroll.set_min_content_width(370)
        listbox=Gtk.ListBox()
        listbox.add_css_class("boxed-list")
        scroll.set_child(listbox);content.append(scroll)
        navigation=stack_box(horizontal=True,spacing=8)
        back=Gtk.Button(label="←")
        choose=Gtk.Button(label=self.e("select_folder"))
        choose.add_css_class("suggested-action")
        navigation.append(back);navigation.append(choose)
        content.append(navigation)
        def show(path):
            try:folders=backend.list_cloud_directories(path)
            except Exception as err:
                self.dialog(self.e("config_failed"),str(err));return
            current["path"]=path
            heading.set_text(path)
            while (row:=listbox.get_first_child()) is not None:listbox.remove(row)
            for name,fullpath in folders:
                row=Gtk.ListBoxRow()
                child=Gtk.Button(label="▸  "+name)
                child.add_css_class("flat")
                child.connect("clicked",lambda _button,target=fullpath:show(target))
                row.set_child(child)
                listbox.append(row)
        def move_back(_button):
            path=current["path"]
            if path=="/my-files":return
            parent=path.rsplit("/",1)[0]
            show(parent if parent.startswith("/my-files") else "/my-files")
        def accept(_button):
            path=current["path"]
            if path=="/my-files":return
            buf=priority_field.get_buffer()
            existing=buf.get_text(buf.get_start_iter(),buf.get_end_iter(),False).strip()
            addition=path[len("/my-files/"):]
            text=existing+"\n"+addition if existing else addition
            buf.set_text(text)
            dialog.close()
        back.connect("clicked",move_back)
        choose.connect("clicked",accept)
        dialog.set_extra_child(content)
        dialog.present(self)
        show("/my-files")

    def choose_folder(self,_button,entry):
        """Open GNOME's native directory picker, verifying the root isn't changed.

        This presents a real selector, but protects the existing root and
        refuses to silently remap 10k tracked files.
        """
        picker=Gtk.FileDialog(title=self.e("select_folder"))
        def selected(dialog,result):
            try:
                chosen=dialog.select_folder_finish(result)
                path=Path(chosen.get_path()).resolve()
                if path!=routing.ROOT:
                    self.dialog(self.t("error"),self.e("root_locked"))
                    return
                entry.set_text(str(path))
            except GLib.Error:
                pass
        picker.select_folder(self,None,selected)

    def make_activity(self):
        """Build a localized activity feed from bounded metadata-only events."""
        outer=stack_box(spacing=16);outer.set_margin_top(28);outer.set_margin_start(22);outer.set_margin_end(22)
        outer.set_margin_bottom(28)
        self.activity_heading=label(self.t("last_events"),"page-heading");outer.append(self.activity_heading)
        self.activity_info=label(self.t("no_events"),"muted")
        outer.append(self.activity_info)
        self.activity_group=Adw.PreferencesGroup();outer.append(self.activity_group)
        self.activity_rows=[]
        return outer
    def make_settings(self):
        """Build language and exclusion controls without exposing credentials."""
        outer=stack_box(spacing=18);outer.set_margin_top(28);outer.set_margin_start(22);outer.set_margin_end(22)
        outer.set_margin_bottom(26)
        self.settings_heading=label(self.t("settings"),"page-heading");outer.append(self.settings_heading)
        group=Adw.PreferencesGroup()
        self.language_row=Adw.ComboRow(title=self.t("language"))
        choices=Gtk.StringList.new([self.t("system"),self.t("german"),self.t("english")])
        self.language_row.set_model(choices)
        self.language_row.set_selected({"system":0,"de":1,"en":2}.get(self.app.language_setting,0))
        self.language_row.connect("notify::selected",self.change_language)
        group.add(self.language_row);outer.append(group)
        rules=Adw.PreferencesGroup()
        self.file_rule=Adw.EntryRow(title=self.t("patterns"))
        self.dir_rule=Adw.EntryRow(title=self.t("directory_names"))
        rules.add(self.file_rule);rules.add(self.dir_rule)
        current=backend.settings().get("exclusions",{})
        self.file_rule.set_text(", ".join(current.get("file_patterns",[])))
        self.dir_rule.set_text(", ".join(current.get("directory_names",[])))
        self.exclusions_heading=label(self.t("exclusions"),"section-label")
        outer.append(self.exclusions_heading);outer.append(rules)
        self.exclusion_hint=label(self.t("only_new"),"muted",True);outer.append(self.exclusion_hint)
        self.save_button=Gtk.Button(label=self.t("save"));self.save_button.add_css_class("suggested-action")
        self.save_button.connect("clicked",self.save_rules);outer.append(self.save_button)
        self.safety_heading=label(self.t("safety"),"section-label");outer.append(self.safety_heading)
        self.settings_safety=label(self.t("safety_hint"),"muted",True);outer.append(self.settings_safety)
        return outer
    def dialog(self,title,body):
        """Display a localized notice or actionable failure."""
        d=Adw.AlertDialog(heading=title,body=body)
        d.add_response("close",self.t("close"))
        d.present(self)
    def sync_now(self,*_):
        """Ask systemd to run the existing local-to-cloud safe sync service."""
        self._request_sync(backend.request_local_sync)
    def sync_full_now(self,*_):
        """Ask systemd to run the full two-way scan, preserving its safety lock."""
        self._request_sync(backend.request_full_sync)
    def _request_sync(self,callback):
        """Report only a request acknowledgement, never an unverified sync result."""
        try:
            result=callback()
            if result.returncode:
                self.dialog(self.t("error"),result.stderr[-300:] or self.t("cannot_start"))
            else:
                self.dialog(self.t("success"),self.a("started_only"))
        except Exception as ex:self.dialog(self.t("error"),str(ex))
    def save_rules(self,*_):
        """Validate and atomically save new-file exclusion rules."""
        try:
            patterns=[x.strip() for x in self.file_rule.get_text().split(",") if x.strip()]
            dirs=[x.strip() for x in self.dir_rule.get_text().split(",") if x.strip()]
            backend.save_exclusions(patterns,dirs)
            backend.restart_watcher()
            self.dialog(self.t("success"),self.t("saved"))
        except Exception as ex:self.dialog(self.t("save_failed"),str(ex))
    def change_language(self,*_):
        """Rebuild the interface in the newly selected language."""
        idx=self.language_row.get_selected()
        new=("system","de","en")[idx]
        if new==self.app.language_setting:return
        save_language(new);self.app.language_setting=new
        self.app.language=preferred() if new=="system" else new
        page=self.tabs.get_visible_child_name()
        self.set_content(None)
        # Build a fresh localized window; keep selection.
        successor=Window(self.app)
        successor.tabs.set_visible_child_name(page)
        successor.present()
        self.close()
    def refresh(self):
        """Refresh only the selected runtime mode; never cross into production."""
        if getattr(self.app,"public_alpha",False):
            return True
        data=backend.snapshot()
        healthy=data["healthy"]
        watcher_active=data["services"].get("watcher") is True
        watcher_enabled=backend.watcher_enabled()
        self._updating_monitor_switch=True
        try:
            self.monitor_switch.set_state(watcher_enabled and watcher_active)
            self.monitor_switch.set_active(watcher_enabled and watcher_active)
        finally:
            self._updating_monitor_switch=False
        self.local_status.set_subtitle(self.d("local_on") if watcher_active else self.d("local_off"))
        self._updating_cloud_switch=True
        try:
            self.cloud_switch.set_state(backend.cloud_monitor_enabled())
            self.cloud_switch.set_active(backend.cloud_monitor_enabled())
        finally:
            self._updating_cloud_switch=False
        cloud_timer=data["services"].get("cloud_timer") is True
        full_timer=data["services"].get("full_timer") is True
        self.cloud_status.set_subtitle(self.d("cloud_on") if cloud_timer and full_timer else self.d("cloud_off"))
        full_record=data.get("full") or {}
        try:
            from datetime import datetime,timezone
            parsed=datetime.strptime(full_record["time"],"%Y-%m-%dT%H:%M:%S%z")
            freshness=(datetime.now(timezone.utc)-parsed.astimezone(timezone.utc)).total_seconds()
        except (KeyError,TypeError,ValueError):
            freshness=None
        interval=routing.load()["interval_minutes"]["full"]
        full_ok=full_timer and freshness is not None and freshness <= max(3*interval*60,10800) and not full_record.get("errors",0) and not full_record.get("conflicts",0)
        all_ok=(full_ok and cloud_timer and watcher_active and healthy is not False)
        full_running=bool(data.get("full_running"))
        self.hero_title.set_text(
            self.d("running_headline") if full_running
            else self.d("headline") if all_ok else self.d("attention"))
        verified=data.get("full_last_success")
        self.full_health_detail.set_text(
            self.d("last_full").format(time=verified.strftime("%d.%m.%Y, %H:%M"))
            if verified else self.d("status_unknown"))
        next_run=data.get("full_next_scheduled")
        if data.get("full_running"):
            self.next_full_detail.set_text(self.d("currently_running"))
        elif next_run:
            from datetime import datetime as _Datetime
            next_display=_Datetime.strptime(next_run,"%Y-%m-%d %H:%M").strftime("%d.%m.%Y, %H:%M")
            self.next_full_detail.set_text(self.d("next_full").format(time=next_display))
        else:
            self.next_full_detail.set_text(
                self.d("next_disabled") if not full_timer else self.d("next_unknown"))
        self.monitor_icon.set_from_icon_name(
            "view-refresh-symbolic" if full_running
            else "emblem-ok-symbolic" if all_ok else "dialog-warning-symbolic")
        if all_ok:
            self.monitor_hero.remove_css_class("hero-offline")
        else:
            self.monitor_hero.add_css_class("hero-offline")
        if healthy is False:
            self.monitor_health.set_text("; ".join(data.get("issues",[]))[:175])
            self.monitor_health.set_visible(True)
        else:
            self.monitor_health.set_visible(False)
        self.metric_widgets["tracked"][1].set_text(f'{data["tracked"]:,}'.replace(",","." ))
        self.metric_widgets["waiting"][1].set_text(str(data["pending"] if data["pending"] is not None else "—"))
        current_errors=(data["quick"].get("conflicts",0)+data["full"].get("conflicts",0))
        self.metric_widgets["conflicts"][1].set_text(str(current_errors))
        config=routing.load()
        for index,route in enumerate(self.route_widgets):
            minutes=config["interval_minutes"][("local","priority","full")[index]]
            route["cadence"].set_subtitle(self.u("cadence").format(minutes=minutes))
        self.update_running()
        for row,key in ((self.local_row,"quick"),(self.cloud_row,"priority"),(self.full_row,"full")):
            row.set_subtitle(data[key].get("time",self.t("unknown")))
        self.activity_info.set_text(self.t("updated")+": "+data["captured_at"])
        for row in self.activity_rows:self.activity_group.remove(row)
        self.activity_rows=[]
        for event in data["events"]:
            kind=event.get("event","")
            when=event.get("time","")
            detail=event.get("path",event.get("destination",event.get("source","")))
            if not detail:
                detail=", ".join(f"{key}: {event[key]}" for key in ("uploaded","downloaded","conflicts","errors") if key in event)
            row=Adw.ActionRow(title=event_label(self.app.language,kind),subtitle=str(when)+"  ·  "+str(detail)[:100])
            self.activity_group.add(row)
            self.activity_rows.append(row)
        return True
class Application(Adw.Application):
    def __init__(self,lang_override=None,public_alpha=False):
        """Configure the existing desktop or an explicitly requested safe alpha preview."""
        super().__init__(application_id=APP_ID,flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.public_alpha=bool(public_alpha)
        self.language_setting=lang_override or ("system" if public_alpha else backend.read_json(LANG).get("language","system"))
        self.language=preferred() if self.language_setting=="system" else self.language_setting
    def do_activate(self):
        """Apply GNOME styling once and present the native window."""
        display=Gdk.Display.get_default()
        if display and not getattr(self,"_css_loaded",False):
            provider=Gtk.CssProvider()
            provider.load_from_data(CSS.encode("utf-8"))
            Gtk.StyleContext.add_provider_for_display(display,provider,Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            self._css_loaded=True
        win=self.props.active_window
        if win:win.present()
        else:Window(self).present()
def main():
    """Run the graphical app or its safe localization/backend self-check."""
    validate()
    if "--self-test" in sys.argv:
        print("L10N_OK",validate())
        print("BACKEND_OK",len(backend.UNITS))
        return 0
    override=None
    if "--lang=de" in sys.argv:override="de"
    if "--lang=en" in sys.argv:override="en"
    return Application(override,public_alpha="--public-alpha" in sys.argv).run([sys.argv[0]])
if __name__=="__main__":raise SystemExit(main())
