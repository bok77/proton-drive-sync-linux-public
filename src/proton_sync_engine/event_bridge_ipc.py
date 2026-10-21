"""Bounded local JSON-line bridge into private pending state; no network or ACK."""
import json
from .event_bridge_spool import stage_batch, BridgeBlocked

MAX_LINE_BYTES=8192

def ingest_line(state_dir, scope, line):
    if not isinstance(line,(bytes,bytearray)) or len(line)>MAX_LINE_BYTES:
        raise BridgeBlocked('ipc_line_invalid_or_oversized')
    try:
        msg=json.loads(line.decode('utf-8','strict'))
    except (UnicodeError,ValueError) as exc:
        raise BridgeBlocked('ipc_invalid_json') from exc
    if not isinstance(msg,dict) or set(msg)!={'type','scope','event'} or msg['type']!='sdk_event' or msg['scope']!=scope:
        raise BridgeBlocked('ipc_invalid_envelope')
    event=msg['event']
    if not isinstance(event,dict) or set(event)!={'type','treeEventScopeId','eventId','nodeUid'}:
        raise BridgeBlocked('ipc_invalid_fields')
    return stage_batch(state_dir,scope,[event])
