import json,tempfile,unittest
from pathlib import Path
from proton_sync_engine.v1_run_result import baseline_lines,result_after
class EvidenceTests(unittest.TestCase):
 def test_only_new_run_end_counts(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'events.jsonl'; record={'event':'run_end','uploaded':1,'remote_downloaded':2,'valid':0,'conflicts':0,'errors':0}
   path.write_text(json.dumps(record)+'\n')
   marker=baseline_lines(tmp)
   self.assertEqual(result_after(tmp,marker)['status'],'PENDING')
   path.write_text(path.read_text()+json.dumps(record)+'\n')
   self.assertEqual(result_after(tmp,marker)['status'],'SUCCESS')
 def test_conflict_is_not_success(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'events.jsonl';path.write_text(json.dumps({'event':'run_end','uploaded':0,'remote_downloaded':0,'valid':1,'conflicts':1,'errors':0})+'\n')
   self.assertEqual(result_after(tmp,0)['status'],'ATTENTION')
 def test_missing_or_invalid_never_success(self):
  with tempfile.TemporaryDirectory() as tmp:
   self.assertEqual(result_after(tmp,0)['status'],'PENDING')
   (Path(tmp)/'events.jsonl').write_text('{bad}\n'+json.dumps({'event':'run_end','uploaded':1})+'\n')
   self.assertEqual(result_after(tmp,0)['status'],'UNKNOWN')
