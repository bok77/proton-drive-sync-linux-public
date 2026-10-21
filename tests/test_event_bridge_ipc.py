import json,tempfile,unittest
from pathlib import Path
from proton_sync_engine.event_bridge_ipc import ingest_line,MAX_LINE_BYTES
from proton_sync_engine.event_bridge_spool import initialize_cursor,BridgeBlocked
class IPCContractTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)/'state';self.root.mkdir(mode=0o700)
        initialize_cursor(self.root,'scope','base')
        self.item={'type':'sdk_event','scope':'scope','event':{'type':'node_updated','treeEventScopeId':'scope','eventId':'e1','nodeUid':'n1'}}
    def test_valid_line_spools_without_ack(self):
        r=ingest_line(self.root,'scope',json.dumps(self.item).encode())
        self.assertEqual(r.next_cursor,'e1')
        self.assertIn('base',(self.root/'cursor.json').read_text())
        with self.assertRaises(BridgeBlocked):ingest_line(self.root,'scope',json.dumps(self.item).encode())
    def test_untrusted_envelopes_fail_closed(self):
        for blob in (b'not-json',b'\xff',b' '* (MAX_LINE_BYTES+1),json.dumps({**self.item,'secret':'bad'}).encode(),
                     json.dumps({**self.item,'scope':'other'}).encode(),
                     json.dumps({**self.item,'event':{**self.item['event'],'secret':'bad'}}).encode()):
            with self.assertRaises(BridgeBlocked):ingest_line(self.root,'scope',blob)
        self.assertFalse((self.root/'pending.json').exists())
