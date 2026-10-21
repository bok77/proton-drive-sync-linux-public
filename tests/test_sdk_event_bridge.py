import tempfile,unittest
from pathlib import Path
from proton_sync_engine.sdk_event_bridge import EventSubscriptionBridge
from proton_sync_engine.event_bridge_spool import initialize_cursor, BridgeBlocked

class SDKEventBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.state=Path(self.tmp.name)/'bridge';self.state.mkdir(mode=0o700)
        initialize_cursor(self.state,'scope','base')
    def test_fake_sdk_subscription_stages_and_never_advances(self):
        callbacks=[]
        def subscribe(scope,cb):
            self.assertEqual(scope,'scope');callbacks.append(cb);return object()
        bridge=EventSubscriptionBridge(self.state,'scope',subscribe)
        bridge.start()
        callbacks[0]([{'type':'node_updated','treeEventScopeId':'scope','eventId':'next','nodeUid':'item'}])
        self.assertTrue((self.state/'pending.json').exists())
        self.assertIn('base',(self.state/'cursor.json').read_text())
        with self.assertRaises(BridgeBlocked):callbacks[0]([{'type':'node_updated','treeEventScopeId':'scope','eventId':'later','nodeUid':'item'}])
        with self.assertRaises(BridgeBlocked):bridge.start()
    def test_unconfirmed_subscription_is_blocked(self):
        bridge=EventSubscriptionBridge(self.state,'scope',lambda *_:None)
        with self.assertRaises(BridgeBlocked):bridge.start()
