"""Read-only V1 run evidence. Never infer success from a systemd start request."""
import json
from pathlib import Path

def result_after(state_dir, started_at):
    """Return a verified completion after the prior event-line marker, or PENDING."""
    path=Path(state_dir)/'events.jsonl'
    if not path.is_file() or path.is_symlink():
        return {'status':'PENDING'}
    try:
        records=path.read_text(encoding='utf-8').splitlines()
    except OSError:
        return {'status':'UNKNOWN'}
    # No trustworthy per-run ID/timestamp in legacy events. Require a newly
    # appended run_end after a captured byte/line position instead.
    for line in reversed(records[started_at:]):
        try: item=json.loads(line)
        except (ValueError,TypeError):continue
        if item.get('event')!='run_end':continue
        values={}
        for key in ('uploaded','remote_downloaded','valid','conflicts','errors'):
            value=item.get(key)
            if type(value)!=int or value<0:return {'status':'UNKNOWN'}
            values[key]=value
        return {'status':'SUCCESS' if not (values['errors'] or values['conflicts']) else 'ATTENTION',**values}
    return {'status':'PENDING'}

def baseline_lines(state_dir):
    """Count existing event lines before starting an isolated run."""
    path=Path(state_dir)/'events.jsonl'
    if not path.is_file() or path.is_symlink():return 0
    try:return len(path.read_text(encoding='utf-8').splitlines())
    except OSError:return 0
