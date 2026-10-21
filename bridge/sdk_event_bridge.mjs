// Boundary for an official SDK subscription. No credentials, cloud login or
// provider import is performed by this executable. Injection is mandatory.
export function createEventRelay({ subscribe, scopeId, emit, onBlocked }) {
  if (typeof subscribe !== 'function' || typeof emit !== 'function' ||
      typeof onBlocked !== 'function' || typeof scopeId !== 'string' || !scopeId) {
    throw new Error('bridge_configuration_required');
  }
  let blocked = false;
  let subscription;
  async function receive(event) {
    if (blocked) return;
    try {
      if (!event || event.treeEventScopeId !== scopeId ||
          !['node_created','node_updated','node_deleted'].includes(event.type) ||
          typeof event.eventId !== 'string' || !event.eventId ||
          typeof event.nodeUid !== 'string' || !event.nodeUid) {
        throw new Error('unsupported_or_invalid_event');
      }
      await emit({ type: 'sdk_event', scope: scopeId, event: {
        type:event.type, treeEventScopeId:event.treeEventScopeId,
        eventId:event.eventId, nodeUid:event.nodeUid
      }});
    } catch (_) {
      blocked = true;
      try { await subscription?.dispose?.(); } catch (_) { /* fail closed */ }
      await onBlocked('EVENT_BRIDGE_BLOCKED');
    }
  }
  return {
    async start() {
      if (blocked || subscription) throw new Error('subscription_unavailable');
      subscription = await subscribe(receive);
      if (!subscription || typeof subscription.dispose !== 'function') {
        blocked = true;
        throw new Error('subscription_not_confirmed');
      }
    },
    async stop() {
      blocked = true;
      await subscription?.dispose?.();
    },
    get blocked() { return blocked; }
  };
}
