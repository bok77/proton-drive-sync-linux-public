import unittest
from proton_sync_engine.event_cursor_contract import validate_batch,EventCursorBlocked

class EventCursorContractTests(unittest.TestCase):
    def test_two_valid_node_events(self):
        events=[{'type':'node_created','treeEventScopeId':'scope','eventId':'next1','nodeUid':'n1'},
                {'type':'node_updated','treeEventScopeId':'scope','eventId':'next2','nodeUid':'n2'}]
        b=validate_batch('scope','base',events)
        self.assertEqual(b.next_cursor,'next2')
        self.assertEqual(b.node_ids,('n1','n2'))
    def test_empty_batch_does_not_advance(self):
        self.assertEqual(validate_batch('scope','base',[]).next_cursor,'base')
    def test_unsafe_events_block(self):
        base={'type':'node_created','treeEventScopeId':'scope','eventId':'next','nodeUid':'n'}
        for change in ({'type':'fast_forward'},{'type':'tree_refresh'},{'treeEventScopeId':'other'},
                       {'eventId':'base'},{'eventId':None},{'nodeUid':None}):
            with self.assertRaises(EventCursorBlocked):validate_batch('scope','base',[{**base,**change}])
        with self.assertRaises(EventCursorBlocked):validate_batch('scope','base',[base,base])
        with self.assertRaises(EventCursorBlocked):validate_batch('scope','',[])
