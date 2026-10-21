"""Synthetic absence/rename safety regression: never silently destroy data."""
from test_portable_engine_e2e import PortableEngineIntegrationTests

class RenameDeleteSafety(PortableEngineIntegrationTests):
    def test_cloud_deleted_after_pairing_does_not_silently_erase_local(self):
        name='Inbox/important.txt'
        self.cloud.put(name,b'important')
        local=self.root/name
        local.write_bytes(b'important')
        self.ancestor(name)
        del self.cloud.content[name]
        del self.cloud.revisions[name]
        self.run_engine()
        self.assertTrue(local.exists(), 'Remote absence must not silently erase local file')
        self.assertEqual(local.read_bytes(),b'important')

    def test_local_rename_does_not_silently_erase_remote_original(self):
        name='Inbox/original.txt'
        self.cloud.put(name,b'important')
        local=self.root/name
        local.write_bytes(b'important')
        self.ancestor(name)
        local.rename(self.root/'Inbox/renamed.txt')
        self.run_engine()
        self.assertEqual(self.cloud.content[name],b'important')
