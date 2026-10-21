"""Integration tests for the read-only inventory runner (synthetic data only)."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

SRC=Path(__file__).resolve().parents[1]/"scripts/preview_bidirectional.py"
spec=importlib.util.spec_from_file_location("preview_runner",SRC)
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

def sha(x):
    return hashlib.sha1(x).hexdigest()

def meta(content,rev):
    return {"activeRevision":{"uid":rev,"claimedSize":len(content),
                               "claimedDigests":{"sha1":sha(content)}}}

class Exclusion:
    def excluded(self,*args,**kwargs):
        return False

class FullDryRunTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"root"
        self.state=Path(self.temp.name)/"state"
        self.state.mkdir()
        for top in runner.TOP:(self.root/top).mkdir(parents=True)
        self.base=self.state/"baseline.json"
        self.fixture="00_Inbox/test.txt"
        (self.root/self.fixture).write_bytes(b"local-new")
        self.base.write_text(json.dumps({self.fixture:{"sha1":sha(b"old"),"revision":"r1"}}))
        self.module=SimpleNamespace(exc=Exclusion(),
             remote_digest=lambda m:m["activeRevision"]["claimedDigests"]["sha1"],
             meta_rev=lambda m:m["activeRevision"]["uid"],
             checked_remote=lambda m:True)
    def call(self,manifest,errors=None,write=False):
        with patch.object(runner,"production",return_value=self.module), \
             patch.object(runner.subprocess,"run",return_value=SimpleNamespace(returncode=0)),\
             patch.object(runner,"REPORT",self.state/"result.json"), \
             patch.object(runner,"STATE",self.state):
            return runner.analyze(scan=lambda:(manifest,{},errors or []),
                                  root=self.root,baseline_file=self.base,write=write)
    def test_positive_local_upload_proposal_without_file_change(self):
        self.module.checked_remote=lambda m:True
        before=(self.root/self.fixture).read_bytes()
        result=self.call({self.fixture:meta(b"old","r1")},write=True)
        self.assertEqual(result["counts"],{"upload":1})
        self.assertTrue(result["cloud_changes_included"])
        self.assertEqual((self.root/self.fixture).read_bytes(),before)
        self.assertTrue((self.state/"result.json").exists())
    def test_negative_incomplete_cloud_scan_fails_closed(self):
        with self.assertRaisesRegex(RuntimeError,"Incomplete remote inventory"):
            self.call({},errors=[{"problem":"timeout"}],write=True)
        self.assertFalse((self.state/"result.json").exists())
    def test_negative_cloud_missing_not_auto_deleted(self):
        result=self.call({})
        self.assertEqual(result["counts"],{"conflict":1})
        self.assertTrue((self.root/self.fixture).exists())
    def test_positive_remote_new_file_download_proposal(self):
        result=self.call({self.fixture:meta(b"local-new","r2"),
                          "00_Inbox/remote.txt":meta(b"cloud","r7")})
        self.assertEqual(result["counts"],{"download":1})
        self.assertFalse((self.root/"00_Inbox/remote.txt").exists())
    def test_negative_baseline_drift_blocks_preview(self):
        def scan():
            self.base.write_text('{"mutated":{}}')
            return {self.fixture:meta(b"old","r1")},{},[]
        with patch.object(runner,"production",return_value=self.module),\
             patch.object(runner.subprocess,"run",return_value=SimpleNamespace(returncode=0)):
            with self.assertRaisesRegex(RuntimeError,"Baseline drift"):
                runner.analyze(scan=scan,root=self.root,baseline_file=self.base,write=False)

if __name__=="__main__":unittest.main()
