"""Three-way classifier regressions: safe preview semantics, no mutation."""
import unittest
from proton_sync_desktop.analyze import classify,summarize

A={"sha1":"old","revision":"r1"}

def case(local,remote,revision="r1",ancestor=A,exists_local=True,exists_remote=True,**kwargs):
    return classify("00_Inbox/example.txt",ancestor,local,remote,revision,
                    local_exists=exists_local,remote_exists=exists_remote,**kwargs)

class ChangeClassificationTests(unittest.TestCase):
    def test_positive_only_local_changed_upload(self):
        self.assertEqual(case("new","old")["action"],"upload")
    def test_positive_only_cloud_changed_download(self):
        self.assertEqual(case("old","new","r2")["action"],"download")
    def test_positive_new_cloud_file(self):
        self.assertEqual(case(None,"cloud","r2",ancestor=None,exists_local=False)["action"],"download")
    def test_positive_new_local_file(self):
        self.assertEqual(case("local",None,ancestor=None,exists_remote=False)["action"],"upload")
    def test_negative_both_changed_conflict(self):
        self.assertEqual(case("local2","cloud2","r2")["action"],"conflict")
    def test_negative_cloud_deletion_delayed(self):
        result=case("old",None,exists_remote=False)
        self.assertEqual(result["action"],"pending_cloud_deletion")
    def test_negative_local_deletion_delayed(self):
        result=case(None,"old",exists_local=False)
        self.assertEqual(result["action"],"pending_local_deletion")
    def test_negative_remote_modified_local_deleted(self):
        self.assertEqual(case(None,"new","r2",exists_local=False)["action"],"conflict")
    def test_negative_symlink_conflict(self):
        self.assertEqual(case(None,"old",local_regular=False)["action"],"conflict")
    def test_negative_untrusted_remote_checksum(self):
        self.assertEqual(case("old",None,remote_valid=False)["action"],"conflict")
    def test_negative_untracked_duplicate_not_overwritten(self):
        self.assertEqual(case("a","b","r2",ancestor=None)["action"],"conflict")
    def test_same_checksum_reconciled(self):
        self.assertEqual(case("same","same","r2")["action"],"unchanged")
    def test_counts(self):
        self.assertEqual(summarize([case("new","old"),case("old","new","r2")]),
                         {"upload":1,"download":1})

if __name__=="__main__":unittest.main()
