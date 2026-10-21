"""Injected SDK subscription boundary, synthetic only; never opens a Proton session.

A real adapter must supply subscribe(scope, callback); callbacks only stage
validated event batches, they cannot acknowledge or mutate synced files.
"""
from __future__ import annotations
from .event_bridge_spool import stage_batch, BridgeBlocked

class EventSubscriptionBridge:
    def __init__(self, state_dir, scope_id, subscribe):
        if not callable(subscribe):
            raise TypeError('subscription_adapter_required')
        self.state_dir=state_dir
        self.scope_id=scope_id
        self.subscribe=subscribe
        self.handle=None

    def on_events(self, events):
        # Fail closed; a future real SDK adapter must catch this exception,
        # dispose its subscription and surface a safe blocked status.
        try:
            stage_batch(self.state_dir,self.scope_id,events)
        except BridgeBlocked:
            raise

    def start(self):
        if self.handle is not None:
            raise BridgeBlocked('subscription_already_started')
        self.handle=self.subscribe(self.scope_id,self.on_events)
        if self.handle is None:
            raise BridgeBlocked('subscription_not_confirmed')
        return self.handle
