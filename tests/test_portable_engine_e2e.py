"""Synthetic end-to-end proof of the *actual* portable full-sync algorithm.

Network and mount probing are replaced by an in-memory fake Proton CLI and
a synthetic mounted filesystem. No real Proton commands, systemd units, or
personal file trees can be reached. Engine files are imported only after
portable_paths.paths has been patched to a disposable root.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


RUNTIME=Path(__file__).resolve().parents[1]/"src/proton_sync_engine/runtime"

class FakeCloud:
    def __init__(self):
        self.content={}
        self.revisions={}
        self.requests=[]
        self.fail_download=False
    def put(self,name,data:bytes):
        self.content[name]=data
        self.revisions[name]=str(int(self.revisions.get(name,"0"))+1)
    def meta(self,name):
        data=self.content[name]
        return {
            "type":"file",
            "name":{"ok":True,"value":name.split("/")[-1]},
            "activeRevision":{
                "uid":self.revisions[name],
                "claimedSize":len(data),
                "claimedDigests":{"sha1":hashlib.sha1(data).hexdigest()},
            },
        }
    def cli(self,*args,timeout=300):
        self.requests.append(tuple(args))
        if args[:2]==("filesystem","list"):
            path=args[2].removeprefix("/my-files/")
            items=[self.meta(key) for key in sorted(self.content)
                   if key.startswith(path+"/") and "/" not in key[len(path)+1:]]
            return SimpleNamespace(returncode=0,stdout=json.dumps(items),stderr="")
        if args[:2]==("filesystem","info"):
            path=args[2].removeprefix("/my-files/")
            if path not in self.content:
                return SimpleNamespace(returncode=1,stdout="",stderr="absent")
            return SimpleNamespace(returncode=0,stdout=json.dumps(self.meta(path)),stderr="")
        if args[:2]==("filesystem","upload"):
            source=Path(args[-2])
            dest=args[-1].removeprefix("/my-files/")
            name=dest+"/"+source.name
            if args[3]=="skip" and name in self.content:
                # Real Proton CLI 0.9.0 returns success with Skipped: 1.
                return SimpleNamespace(returncode=0,stdout="Uploaded: 0 items\nSkipped: 1 items",stderr="")
            self.put(name,source.read_bytes())
            return SimpleNamespace(returncode=0,stdout="",stderr="")
        if args[:2]==("filesystem","download"):
            if self.fail_download:
                return SimpleNamespace(returncode=1,stdout="",stderr="network failure")
            cloudpath=args[-2].removeprefix("/my-files/")
            target=Path(args[-1])/Path(cloudpath).name
            target.write_bytes(self.content[cloudpath])
            return SimpleNamespace(returncode=0,stdout="",stderr="")
        return SimpleNamespace(returncode=1,stdout="",stderr="unexpected fake API")


class PortableEngineIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="portable-sync-e2e-")
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name)
        self.root=self.base/"synthetic-mount"/"Sync"
        (self.root/"Inbox").mkdir(parents=True)
        self.state=self.base/"private-state"
        self.state.mkdir(mode=0o700)
        self.cloud=FakeCloud()
        self.config=SimpleNamespace(
            local_root=self.root,
            mount_root=self.root.parent,
            state_dir=self.state,
            verify_state=self.base/"verify",
            exclusion_settings=self.base/"settings.json",
            cli_executable=self.base/"FAKE-NEVER-INVOKED",
            managed_folders=("Inbox",),
            priority_folders=("Inbox",),
            _allow_unverified_pairing_in_synthetic_tests=True,
        )
        from proton_sync_engine import portable_paths
        with patch.object(portable_paths,"paths",return_value=self.config):
            spec=importlib.util.spec_from_file_location("synthetic_bisync",RUNTIME/"proton-bisync.py")
            self.engine=importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.engine)
        self.engine.v.cli=self.cloud.cli
        # Historic transfer tests model a hypothetical atomic-capable provider.
        # No such capability is enabled in the actual CLI/runtime.
        guard=patch("proton_sync_engine.existing_revision_guard.require_atomic_revision_update",return_value=None)
        guard.start()
        self.addCleanup(guard.stop)
        self.engine.exc.excluded=lambda *args,**kwargs:False
        self.engine._progress.update=lambda *args,**kwargs:None

    def run_engine(self):
        with patch.object(self.engine.subprocess,"run",return_value=SimpleNamespace(returncode=0)):
            return self.engine.main()

    def ancestor(self,*names):
        data={name:{
            "sha1":hashlib.sha1(self.cloud.content[name]).hexdigest(),
            "revision":self.cloud.revisions[name],
        } for name in names}
        self.engine.BASE.write_text(json.dumps(data))

    def test_missing_baseline_aborts_without_creating_accepted_state(self):
        self.cloud.put("Inbox/test.txt",b"original")
        self.assertEqual(self.run_engine(),42)
        self.assertFalse(self.engine.BASE.exists())
        self.assertFalse(self.cloud.requests, "Pairing gate must precede all cloud calls")
        self.assertEqual(self.cloud.content["Inbox/test.txt"],b"original")

    def test_local_upload_then_restart_is_idempotent(self):
        name="Inbox/test.txt"
        self.cloud.put(name,b"before")
        file=self.root/name
        file.write_bytes(b"before")
        self.ancestor(name)
        file.write_bytes(b"local changed")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.cloud.content[name],b"local changed")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(json.loads(self.engine.BASE.read_text())[name]["sha1"],
                         hashlib.sha1(b"local changed").hexdigest())

    def test_remote_download_then_restart_is_idempotent(self):
        name="Inbox/test.txt"
        self.cloud.put(name,b"before")
        file=self.root/name
        file.write_bytes(b"before")
        self.ancestor(name)
        self.cloud.put(name,b"cloud changed")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(file.read_bytes(),b"cloud changed")
        self.assertEqual(self.run_engine(),0)

    def test_conflicting_edits_leave_both_sides_unchanged(self):
        name="Inbox/test.txt"
        self.cloud.put(name,b"before")
        file=self.root/name
        file.write_bytes(b"before")
        self.ancestor(name)
        self.cloud.put(name,b"cloud edit")
        file.write_bytes(b"local edit")
        self.assertEqual(self.run_engine(),1)
        self.assertEqual(file.read_bytes(),b"local edit")
        self.assertEqual(self.cloud.content[name],b"cloud edit")
        self.assertEqual(json.loads(self.engine.BASE.read_text())[name]["sha1"],
                         hashlib.sha1(b"before").hexdigest())

    def test_new_remote_file_is_downloaded_safely(self):
        self.engine.BASE.write_text("{}")
        self.cloud.put("Inbox/from-cloud.txt",b"new remote")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual((self.root/"Inbox/from-cloud.txt").read_bytes(),b"new remote")
        self.assertEqual(self.run_engine(),0)

    def test_new_local_file_is_uploaded_safely(self):
        self.engine.BASE.write_text("{}")
        (self.root/"Inbox/new-local.txt").write_bytes(b"new local")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.cloud.content["Inbox/new-local.txt"],b"new local")
        self.assertEqual(self.run_engine(),0)

    def test_isolated_install_sync_restart_uninstall(self):
        """Test real staged-unit validation together with the full engine path."""
        from proton_sync_engine import install_plan,test_install
        source=self.base/"staged"
        (source/"units").mkdir(parents=True)
        for kind,name in install_plan.UNIT_NAMES.items():
            (source/"units"/name).write_text(install_plan._service_text(kind))
        info={
            "status":"PREVIEW_ONLY", "activation_authorized":False,
            "local_root":str(self.root),
            "mount_root":str(self.root.parent),
            "state_dir":str(self.state),
            "staged_units":list(install_plan.UNIT_NAMES.values()),
        }
        (source/"INSTALL_NOT_ACTIVATED.json").write_text(json.dumps(info))
        (source/"DO_NOT_ENABLE.txt").write_text(
            "No unit here is ready to enable; installer activation is NOT IMPLEMENTED.")
        destination=self.base/"installed"
        units=self.base/"synthetic-units"
        manifest=test_install.install_test(
            source,destination,units,test_install.APPROVAL)
        self.assertFalse(manifest["activation_authorized"])
        self.assertEqual(test_install.verify_test_install(destination,units),manifest)
        name="Inbox/lifecycle.txt"
        self.cloud.put(name,b"original")
        (self.root/name).write_bytes(b"original")
        self.ancestor(name)
        (self.root/name).write_bytes(b"locally changed")
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.cloud.content[name],b"locally changed")
        self.assertEqual(self.run_engine(),0)
        test_install.uninstall_test(destination,units)
        self.assertFalse(destination.exists())
        self.assertFalse(units.exists())
        self.assertEqual((self.root/name).read_bytes(),b"locally changed")
        self.assertEqual(self.cloud.content[name],b"locally changed")

    def test_failed_cloud_download_preserves_file_and_ancestor(self):
        name="Inbox/test.txt"
        self.cloud.put(name,b"before")
        file=self.root/name
        file.write_bytes(b"before")
        self.ancestor(name)
        self.cloud.put(name,b"cloud changed")
        self.cloud.fail_download=True
        self.assertEqual(self.run_engine(),1)
        self.assertEqual(file.read_bytes(),b"before")
        self.assertEqual(json.loads(self.engine.BASE.read_text())[name]["sha1"],
                         hashlib.sha1(b"before").hexdigest())


if __name__=="__main__":
    unittest.main()
