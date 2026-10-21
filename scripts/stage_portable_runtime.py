"""Build inert path-decoupled runtime candidates from frozen reference sources.

Never installs, imports, or starts the production scripts.
"""
import re
from pathlib import Path
project=Path(__file__).resolve().parents[1]
source=project/"src/proton_sync_engine/reference"
target=project/"src/proton_sync_engine/runtime"
target.mkdir(exist_ok=True)
names=["proton-bisync.py","proton-bisync-quick.py","proton-cloud-priority.py",
"proton-verified-download.py","proton-sync-reconcile.py","proton-sync-watcher.py",
"proton-sync-queue.py","proton-sync-exclusions.py","proton-sync-progress.py",
"proton-sync-health.py","proton-pending-changes.py","proton-sync-status.py"]
for name in names:
    text=(source/name).read_text()
    # Import a fail-closed explicit portable setup, never current Fedora paths.
    match="from pathlib import Path\n"
    assert text.count(match)==1,(name,"no pathlib marker")
    text=text.replace(match,match+"from proton_sync_engine.portable_paths import paths as _load_runtime_paths\n_runtime=_load_runtime_paths()\n",1)
    text=text.replace('Path.home()/".local/bin/', 'Path(__file__).resolve().parent/"')
    text=text.replace('Path.home() / ".local/bin/', 'Path(__file__).resolve().parent / "')
    text=text.replace('Path.home()/".local/state/proton-bisync"', '_runtime.state_dir')
    text=text.replace('Path.home() / ".local/state/proton-verified-download"', '_runtime.verify_state')
    text=text.replace('Path.home()/".config/proton-bisync/settings.json"', '_runtime.exclusion_settings')
    text=text.replace('Path.home()/".local/state/proton-bisync/local_events.sqlite3"', '_runtime.state_dir/"local_events.sqlite3"')
    text=text.replace('Path("/mnt/example-sync-root")','_runtime.local_root')
    text=text.replace('Path("/mnt/example-sync-quarantine")','_runtime.mount_root/".proton-sync-quarantine"')
    text=text.replace('Path.home() / ".local/bin/proton-drive"','_runtime.cli_executable')
    text=text.replace('str(Path.home() / ".local/bin/proton-drive")','str(_runtime.cli_executable)')
    if name=="proton-verified-download.py":
        text=text.replace('CLI = str(Path(__file__).resolve().parent / "proton-drive")','CLI = str(_runtime.cli_executable)')
        assert "CLI = str(_runtime.cli_executable)" in text
    text=text.replace('["mountpoint","-q","/mnt/example-drive"]','["mountpoint","-q",str(_runtime.mount_root)]')
    text=text.replace('["mountpoint", "-q", "/mnt/example-drive"]','["mountpoint", "-q", str(_runtime.mount_root)]')
    text=text.replace('shutil.disk_usage("/mnt/example-drive")','shutil.disk_usage(_runtime.mount_root)')
    text=text.replace('FOLDERS = ["00_Inbox", "10_Private", "20_Records",\n           "30_Learning", "40_Knowledge", "50_Projects",\n           "60_Media", "70_Backups", "80_Vault",\n           "90_Archive"]','FOLDERS = list(_runtime.managed_folders)')
    text=re.sub(r'FOLDERS=\("00_Inbox".*?"90_Archive"\)',"FOLDERS=tuple(_runtime.managed_folders)",text,flags=re.S)
    text=re.sub(r'FOLDERS=\{"00_Inbox".*?"90_Archive"\}',"FOLDERS=set(_runtime.managed_folders)",text,flags=re.S)
    # On priority scanner, remove the GUI source-code path dependency entirely.
    if name=="proton-bisync.py":
        # Initial pairing is an explicit future installer step, never an implicit
        # baseline write by the runtime on an unfamiliar local directory.
        start=text.index("    if old is None:\n        baseline={}; conflicts=[]")
        end=text.index("    baseline=dict(old)",start)
        text=text[:start]+(
            "    if old is None:\n"
            "        log(\"initial_pairing_required\")\n"
            "        _progress.update(\"full\",\"finished\",status=\"error\")\n"
            "        return 42\n"
        )+text[end:]
        # First boot after explicit pairing is verification-only. Standard
        # reconciliation cannot start before a private verified guard exists.
        # The synthetic E2E fixture has a non-configurable test-only bypass.
        text=text.replace(
            "    STATE.mkdir(parents=True,exist_ok=True)\n",
            "    if not getattr(_runtime, '_allow_unverified_pairing_in_synthetic_tests', False):\n"
            "        from proton_sync_engine.initial_activation import check as _check_first_start\n"
            "        pending=STATE/'initial_pairing_pending.json'\n"
            "        verified=STATE/'initial_pairing_verified.json'\n"
            "        if verified.exists():\n"
            "            if verified.is_symlink() or pending.exists() or verified.read_text().strip()!='INITIAL_PAIRING_VERIFIED_V1':\n"
            "                return 43\n"
            "        else:\n"
            "            if not pending.is_file() or pending.is_symlink():\n"
            "                return 43\n"
            "            try:\n"
            "                _check_first_start(ROOT,_runtime.managed_folders,BASE,pending,scan,remote_digest,meta_rev)\n"
            "                descriptor=os.open(verified,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n"
            "                with os.fdopen(descriptor,'w') as marker:\n"
            "                    marker.write('INITIAL_PAIRING_VERIFIED_V1')\n"
            "                    marker.flush();os.fsync(marker.fileno())\n"
            "                pending.unlink()\n"
            "                return 0  # no transfers or reconciliation during first startup\n"
            "            except Exception as error:\n"
            "                print('INITIAL_PAIRING_BLOCKED: '+type(error).__name__,flush=True)\n"
            "                return 43\n"
            "    STATE.mkdir(parents=True,exist_ok=True)\n",
            1)
        main_header="def main():\n"
        assert text.count(main_header)==1
        text=text.replace(main_header,
            main_header+
            '    if not BASE.is_file():\n'
            '        return 42  # explicit pairing required; no cloud reads or state writes\n',1)
        # Serialize the ENTIRE runtime, not only the first-boot marker change.
        # No other pairing/recovery operation may race with live reconciliation.
        text=text.replace(
            'if __name__=="__main__":\n',
            'from proton_sync_engine.exclusive_lock import exclusive as _exclusive_runtime_lock\n'
            '_unlocked_runtime_main=main\n'
            'def main():\n'
            '    try:\n'
            '        with _exclusive_runtime_lock(STATE):\n'
            '            return _unlocked_runtime_main()\n'
            '    except (PermissionError, __import__("proton_sync_engine.exclusive_lock",fromlist=["PairingBusy"]).PairingBusy):\n'
            '        return 44  # lock unavailable; never transfer files\n'
            'if __name__=="__main__":\n',
            1)
    if name=="proton-cloud-priority.py":
        start=text.index("# Priority folders are user-editable")
        end=text.index("def main():",start)
        text=text[:start]+'from proton_sync_engine.portable_paths import priority_folders\nFOLDERS=priority_folders(_runtime)\n'+text[end:]
    if name=="proton-sync-status.py":
        text=text.replace('"/usr/bin/python3",str(Path(__file__).resolve().parent/"proton-sync-queue.py")','"/usr/bin/python3",str(Path(__file__).resolve().parent/"proton-sync-queue.py")')
        text=text.replace('print("Cloud-Ablage:  /mnt/example-sync-root")','print("Cloud storage:",_runtime.local_root)')
        text=text.replace('print("Lokale Quarantäne: /mnt/example-sync-quarantine")','print("Local quarantine:",_runtime.mount_root/".proton-sync-quarantine")')
        text=text.replace('Path.home()/".config/proton-bisync/settings.json"','_runtime.exclusion_settings')
    text=text.replace('No /mnt/example-drive mount', 'Configured mount unavailable')
    text=text.replace('/mnt/example-drive is not mounted', 'Configured mount is not mounted')
    text=text.replace('Encrypted /mnt/example-drive not mounted', 'Configured mount not mounted')
    text=text.replace('/mnt/example-drive unavailable', 'Configured mount unavailable')
    text=text.replace('Encrypted /mnt/example-drive missing', 'Configured mount missing')
    text=text.replace('Wenig freier Speicher auf /mnt/example-drive (< 5 GiB)', 'Low free space at configured mount (< 5 GiB)')
    text=text.replace('Speicherplatz von /mnt/example-drive nicht lesbar', 'Unable to read space at configured mount')
    # Never place executable bits on candidate modules.
    (target/name).write_text(text)
print("STAGED_PATH_DECOUPLED_CANDIDATES",len(names))
