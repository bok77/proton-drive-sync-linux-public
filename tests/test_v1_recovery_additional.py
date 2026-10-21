"""Extra V1 fail-closed regression cases; synthetic provider only."""
from test_mvp_failure_matrix import FailureMatrix
from unittest.mock import patch
from proton_sync_engine.existing_revision_guard import AtomicRevisionUnavailable

class V1RecoveryAdditional(FailureMatrix):
    def test_offline_after_local_edit_preserves_both_ends_and_baseline(self):
        name,path=self.setup_pair()
        path.write_bytes(b'local edit held for recovery')
        baseline=self.engine.BASE.read_bytes()
        original=self.cloud.cli
        self.engine.v.cli=lambda *a,**kw: type('Answer',(),{'returncode':1,'stdout':'','stderr':'offline'})()
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b'local edit held for recovery')
        self.assertEqual(self.cloud.content[name],b'before')
        self.assertEqual(self.engine.BASE.read_bytes(),baseline)
        self.engine.v.cli=original
        with patch('proton_sync_engine.existing_revision_guard.require_atomic_revision_update',
                   side_effect=AtomicRevisionUnavailable('conditional_revision_upload_unsupported')):
            self.assertNotEqual(self.run_engine(),0)  # Real V1 revision guard.
        self.assertEqual(path.read_bytes(),b'local edit held for recovery')
        self.assertEqual(self.cloud.content[name],b'before')
        self.assertEqual(self.engine.BASE.read_bytes(),baseline)

    def test_remote_deleted_during_local_edit_keeps_local_copy(self):
        name,path=self.setup_pair()
        baseline=self.engine.BASE.read_bytes()
        path.write_bytes(b'valuable local edit')
        self.cloud.content.pop(name)
        self.cloud.revisions.pop(name)
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b'valuable local edit')
        self.assertEqual(self.engine.BASE.read_bytes(),baseline)
        self.assertNotIn(name,self.cloud.content)

    def test_remote_rename_during_local_edit_does_not_delete_local(self):
        name,path=self.setup_pair()
        baseline=self.engine.BASE.read_bytes()
        path.write_bytes(b'valuable local edit')
        payload=self.cloud.content.pop(name)
        self.cloud.revisions.pop(name)
        renamed='Inbox/renamed.txt'
        self.cloud.put(renamed,payload)
        self.assertNotEqual(self.run_engine(),0)
        self.assertEqual(path.read_bytes(),b'valuable local edit')
        self.assertEqual(self.cloud.content[renamed],b'before')
        # A verified new cloud path may be tracked, but the unresolved
        # original ancestor must not be rewritten or removed.
        import json
        self.assertEqual(json.loads(self.engine.BASE.read_bytes())[name],json.loads(baseline)[name])
