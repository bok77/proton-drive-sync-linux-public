"""Keep a short user-facing V1 gate and preserve technical evidence separately."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class V1AcceptanceMatrixTests(unittest.TestCase):
    def test_short_mvp_gate_and_detail_archive(self):
        short=(ROOT/'docs/V1_PILOT_ACCEPTANCE_MATRIX_20261021.de.md').read_text()
        detail=(ROOT/'docs/V1_PILOT_ACCEPTANCE_MATRIX_DETAIL_20261021.de.md').read_text()
        for word in ('GNOME-App','Datei hochladen','pausieren','NOT ACCEPTED','BLOCKED'):
            self.assertIn(word,short)
        for evidence in ('M1_PARALLEL_REAL_CLI_PROOF_20261021.de.md',
                         'M1_REAL_CLI_COLLISION_PROOF_20261021.de.md',
                         'V1_REMOTE_MISSING_RECOVERY_20261021.de.md',
                         'V1_GTK_REAL_SYSTEMD_VM_PROOF_20261021.de.md'):
            self.assertIn(evidence,detail)
            self.assertTrue((ROOT/'docs'/evidence).is_file())
        self.assertIn('V1_PILOT_ACCEPTANCE_MATRIX_20261021.de.md',(ROOT/'V1.md').read_text())
