import json,tempfile,unittest
from pathlib import Path
from proton_sync_engine.event_bridge_spool import stage_batch,initialize_cursor,BridgeBlocked

class EventBridgeSpoolTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory();self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)/'private';self.root.mkdir(mode=0o700)
    def test_stage_never_advances_cursor_and_recovery_blocks(self):
        initialize_cursor(self.root,'scope','base')
        e=[{'type':'node_updated','treeEventScopeId':'scope','eventId':'next','nodeUid':'node'}]
        self.assertEqual(stage_batch(self.root,'scope',e).next_cursor,'next')
        self.assertEqual(json.loads((self.root/'cursor.json').read_text())['event_id'],'base')
        with self.assertRaisesRegex(BridgeBlocked,'pending_batch'):stage_batch(self.root,'scope',e)
        self.assertEqual((self.root/'pending.json').stat().st_mode & 0o777,0o600)
    def test_missing_or_corrupt_or_world_readable_refuses(self):
        with self.assertRaises(BridgeBlocked):stage_batch(self.root,'scope',[])
        initialize_cursor(self.root,'scope','base')
        p=self.root/'cursor.json';p.chmod(0o644)
        with self.assertRaisesRegex(BridgeBlocked,'unsafe_bridge_state'):stage_batch(self.root,'scope',[])
    def test_refresh_blocks_without_pending(self):
        initialize_cursor(self.root,'scope','base')
        with self.assertRaises(BridgeBlocked):stage_batch(self.root,'scope',[{'type':'tree_refresh','treeEventScopeId':'scope','eventId':'next'}])
        self.assertFalse((self.root/'pending.json').exists())
