"""Pure classification of local/cloud changes against their common ancestor.

No filesystem or network writes are performed by this module. Actions are
proposals for human review, not authorization to perform destructive changes.
"""
from collections import Counter

def classify(path,ancestor,local_sha,remote_sha,remote_revision,
             *,local_exists,remote_exists,remote_valid=True,local_regular=True):
    """Return an explainable, conservative action for a three-way file comparison."""
    base=ancestor or {}
    previous_sha=base.get("sha1")
    previous_rev=base.get("revision")
    if local_exists and not local_regular:
        return {"path":path,"action":"conflict","reason":"unsafe_local_file"}
    if remote_exists and not remote_valid:
        return {"path":path,"action":"conflict","reason":"cloud_digest_unverifiable"}
    if ancestor:
        if not remote_exists:
            if not local_exists:
                return {"path":path,"action":"pending_deletion","reason":"missing_both"}
            if local_sha!=previous_sha:
                return {"path":path,"action":"conflict","reason":"cloud_missing_local_modified"}
            return {"path":path,"action":"pending_cloud_deletion","reason":"remote_missing_safety_delay"}
        if not local_exists:
            if remote_sha==previous_sha and remote_revision==previous_rev:
                return {"path":path,"action":"pending_local_deletion","reason":"local_missing_safety_delay"}
            return {"path":path,"action":"conflict","reason":"local_missing_remote_modified"}
        if local_sha==remote_sha:
            return {"path":path,"action":"unchanged","reason":"both_identical"}
        remote_unchanged=(remote_sha==previous_sha and remote_revision==previous_rev)
        local_unchanged=local_sha==previous_sha
        if remote_unchanged and not local_unchanged:
            return {"path":path,"action":"upload","reason":"local_only_edit"}
        if local_unchanged and not remote_unchanged:
            return {"path":path,"action":"download","reason":"cloud_only_edit"}
        return {"path":path,"action":"conflict","reason":"both_sides_changed"}
    if local_exists and remote_exists:
        if local_sha==remote_sha:
            return {"path":path,"action":"unchanged","reason":"new_identical_on_both"}
        return {"path":path,"action":"conflict","reason":"untracked_file_on_both"}
    if local_exists:
        return {"path":path,"action":"upload","reason":"new_local_file"}
    if remote_exists:
        return {"path":path,"action":"download","reason":"new_cloud_file"}
    return {"path":path,"action":"unchanged","reason":"absent_both"}

def summarize(records):
    """Count preview categories without copying personal file contents."""
    return dict(Counter(row["action"] for row in records))
