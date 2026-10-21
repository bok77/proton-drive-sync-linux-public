"""Isolated recovery matrix for offline, restart and conflicts."""
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from test_portable_engine_e2e import PortableEngineIntegrationTests

class FailureMatrix(unittest.TestCase):
    run_engine=PortableEngineIntegrationTests.run_engine
    ancestor=PortableEngineIntegrationTests.ancestor
    setUp=PortableEngineIntegrationTests.setUp

    def setup_pair(self):
        name="Inbox/restart.txt"
        self.cloud.put(name,b"before")
        path=self.root/name
        path.write_bytes(b"before")
        self.ancestor(name)
        return name,path

    def test_offline_listing_does_not_change_baseline_or_local_files(self):
        name,path=self.setup_pair()
        old=self.engine.BASE.read_bytes()
        original=self.cloud.cli
        def offline(*args,**kwargs):
            if args[:2]==("filesystem","list"):
                return SimpleNamespace(returncode=1,stdout="",stderr="offline")
            return original(*args,**kwargs)
        self.engine.v.cli=offline
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b"before")
        self.assertEqual(self.engine.BASE.read_bytes(),old)
        self.assertEqual(self.cloud.content[name],b"before")

    def test_recovery_after_offline_then_restart(self):
        name,path=self.setup_pair()
        original=self.cloud.cli
        self.engine.v.cli=lambda *a,**kw: SimpleNamespace(returncode=1,stdout="",stderr="offline")
        self.assertNotEqual(self.run_engine(),0)
        self.engine.v.cli=original
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b"before")

    def test_dual_edit_conflict_preserves_data_and_prior_ancestor(self):
        name,path=self.setup_pair()
        before=self.engine.BASE.read_bytes()
        path.write_bytes(b"local conflict")
        self.cloud.put(name,b"cloud conflict")
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b"local conflict")
        self.assertEqual(self.cloud.content[name],b"cloud conflict")
        self.assertEqual(self.engine.BASE.read_bytes(),before)

    def test_download_network_failure_then_retry(self):
        name,path=self.setup_pair()
        self.cloud.put(name,b"new cloud")
        self.cloud.fail_download=True
        before=self.engine.BASE.read_bytes()
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b"before")
        self.assertEqual(self.engine.BASE.read_bytes(),before)
        self.cloud.fail_download=False
        self.assertEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b"new cloud")
        self.assertEqual(self.run_engine(),0)
