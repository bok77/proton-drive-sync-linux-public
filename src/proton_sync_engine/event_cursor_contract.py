"""Pure, fail-closed validation of SDK Drive events; no cloud access or state writes.

Cursor persistence and provider subscription remain separate unapproved gates.
"""
from dataclasses import dataclass

class EventCursorBlocked(ValueError):
    pass

@dataclass(frozen=True)
class EventBatch:
    scope_id: str
    previous_cursor: str
    next_cursor: str
    node_ids: tuple[str, ...]


def validate_batch(scope_id: str, previous_cursor: str, events: list[dict]) -> EventBatch:
    if not isinstance(scope_id, str) or not scope_id or not isinstance(previous_cursor, str) or not previous_cursor:
        raise EventCursorBlocked('missing_cursor_or_scope')
    if not isinstance(events, list):
        raise EventCursorBlocked('invalid_event_batch')
    cursor=previous_cursor
    nodes=[]
    seen=set()
    for event in events:
        if not isinstance(event, dict) or event.get('treeEventScopeId') != scope_id:
            raise EventCursorBlocked('scope_mismatch')
        typ=event.get('type')
        if typ not in ('node_created','node_updated','node_deleted'):
            raise EventCursorBlocked('refresh_or_unknown_event_requires_rebaseline')
        event_id=event.get('eventId')
        node=event.get('nodeUid')
        if not isinstance(event_id,str) or not event_id or not isinstance(node,str) or not node:
            raise EventCursorBlocked('event_identity_missing')
        if event_id==cursor or event_id in seen:
            raise EventCursorBlocked('repeated_event_cursor')
        seen.add(event_id)
        cursor=event_id
        nodes.append(node)
    # Event IDs are opaque. Their monotonicity/continuity cannot be proven here.
    # This validates a batch shape, not absence of upstream missing events.
    return EventBatch(scope_id,previous_cursor,cursor,tuple(nodes))
