import json,subprocess,tempfile,unittest,shutil
from pathlib import Path
from proton_sync_engine.event_bridge_spool import initialize_cursor
from proton_sync_engine.event_bridge_ipc import ingest_line
PROJECT=Path(__file__).resolve().parents[1]
@unittest.skipUnless(shutil.which('node'),'Node runtime not installed')
class SubprocessBridgeTests(unittest.TestCase):
    def test_real_process_boundary_without_provider_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'private';p.mkdir(mode=0o700)
            initialize_cursor(p,'fixture-scope','fixture-base')
            proc=subprocess.run(['node',str(PROJECT/'bridge/sdk_event_ipc_emit_fixture.mjs')],capture_output=True,timeout=8,check=True)
            self.assertEqual(proc.stderr,b'')
            self.assertNotIn(b'NEVER_ECHO',proc.stdout)
            self.assertEqual(len(proc.stdout.splitlines()),1)
            item=ingest_line(p,'fixture-scope',proc.stdout.splitlines()[0])
            self.assertEqual(item.next_cursor,'fixture-next')
            self.assertEqual(json.loads((p/'cursor.json').read_text())['event_id'],'fixture-base')
            self.assertTrue((p/'pending.json').exists())
