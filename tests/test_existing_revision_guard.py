"""Absence of conditional write support must always fail closed."""
import unittest
from proton_sync_engine.existing_revision_guard import (
    AtomicRevisionUnavailable, require_atomic_revision_update,
)

class ExistingRevisionGuardTests(unittest.TestCase):
    def test_unconditional_cloud_update_is_denied(self):
        with self.assertRaisesRegex(AtomicRevisionUnavailable, 'conditional_revision_upload_unsupported'):
            require_atomic_revision_update()
