"""Cloud revision updates require an atomic expected-revision capability.

The presently supported CLI has not demonstrated such an operation. A read
followed by create-new-revision is not atomic. Do not silently downgrade.
"""

class AtomicRevisionUnavailable(RuntimeError):
    pass


def require_atomic_revision_update():
    from .cli_capabilities import require_conditional_existing_write
    require_conditional_existing_write()
