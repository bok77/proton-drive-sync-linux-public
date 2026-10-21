// Official SDK-compatible iterateEvents adapter. An authenticated official SDK
// client must be provided by an isolated future integration; never read CLI auth.
export async function consumeEvents({iterateEvents, scopeId, cursor, emit, signal}) {
  if (typeof iterateEvents !== 'function' || typeof emit !== 'function' ||
      !scopeId || !cursor || !signal) throw Error('iterator_configuration_required');
  let delivered = 0;
  try {
    const iterable = iterateEvents(scopeId, cursor, signal);
    for await (const event of iterable) {
      if (signal.aborted) throw Error('iterator_aborted');
      if (!event || event.treeEventScopeId !== scopeId ||
          !['node_created','node_updated','node_deleted'].includes(event.type) ||
          !event.nodeUid || !event.eventId) throw Error('event_requires_rebaseline');
      // Do not echo the original event: an upstream payload might contain secrets.
      await emit({type:event.type,treeEventScopeId:scopeId,eventId:event.eventId,nodeUid:event.nodeUid});
      delivered++;
    }
    return delivered;
  } catch (_) {
    throw Error('SDK_ITERATOR_BLOCKED');
  }
}
