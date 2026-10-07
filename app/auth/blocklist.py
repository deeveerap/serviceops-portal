"""In-memory token blocklist for logout.

For multi-pod deployments swap this for Redis using settings.REDIS_URL.
"""
from typing import Set

_blocklist: Set[str] = set()


def revoke(token: str) -> None:
    _blocklist.add(token)


def is_revoked(token: str) -> bool:
    return token in _blocklist
