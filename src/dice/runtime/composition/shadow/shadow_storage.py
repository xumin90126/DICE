"""
ShadowStorage — Isolated persistence for Shadow observation records.

Phase 6.1-L1: Provides read/write/clear operations for the
composition_shadow_storage namespace. All records are stored
in-memory with optional JSON export.

Constraints:
    ✅ Uses composition_shadow_storage namespace
    ❌ Never writes to Runtime Storage
    ❌ Never writes to Capability Registry
    ❌ Never writes to Production Database
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class ShadowStorage:
    """Isolated in-memory storage for Shadow runtime records.

    All Shadow records (observations, candidates, validations, traces,
    governance, metrics) are stored in isolated namespaces within this
    storage instance. The storage is intentionally ephemeral (in-memory)
    to prevent accidental persistence in production paths.

    Usage:
        storage = ShadowStorage()
        storage.store("observations", obs_id, obs.to_dict())
        record = storage.load("observations", obs_id)
        all_records = storage.list_records("observations")
    """

    NAMESPACE = "composition_shadow_storage"

    def __init__(self):
        """Initialize empty shadow storage."""
        self._namespaces: Dict[str, Dict[str, Dict[str, Any]]] = {
            "observations": {},
            "candidates": {},
            "validations": {},
            "traces": {},
            "governance": {},
            "metrics": {},
        }
        self._stats: Dict[str, int] = {
            "stores": 0,
            "loads": 0,
            "clears": 0,
        }

    # ── Public API ──

    def store(self, namespace: str, record_id: str, record: Dict[str, Any]) -> None:
        """Store a Shadow record in the given namespace.

        Args:
            namespace: One of "observations"/"candidates"/"validations"/
                       "traces"/"governance"/"metrics"
            record_id: Unique record identifier
            record: Record data as dictionary

        Raises:
            ValueError: If namespace is invalid
            TypeError: If record is not a dict
        """
        self._validate_namespace(namespace)
        if not isinstance(record, dict):
            raise TypeError(
                f"ShadowStorage.store() requires dict, got {type(record).__name__}"
            )

        self._namespaces[namespace][record_id] = record
        self._stats["stores"] += 1

    def load(self, namespace: str, record_id: str) -> Optional[Dict[str, Any]]:
        """Load a Shadow record by ID.

        Args:
            namespace: Storage namespace name
            record_id: Record identifier

        Returns:
            Record dict if found, None otherwise
        """
        self._validate_namespace(namespace)
        self._stats["loads"] += 1
        return self._namespaces[namespace].get(record_id)

    def list_records(
        self, namespace: str, limit: Optional[int] = None
    ) -> List[str]:
        """List all record IDs in a namespace.

        Args:
            namespace: Storage namespace name
            limit: Optional maximum number of IDs to return

        Returns:
            List of record IDs
        """
        self._validate_namespace(namespace)
        ids = list(self._namespaces[namespace].keys())
        if limit is not None and limit > 0:
            return ids[:limit]
        return ids

    def clear(self, namespace: Optional[str] = None) -> int:
        """Clear records from storage.

        Args:
            namespace: Specific namespace to clear, or None for all

        Returns:
            Number of records cleared
        """
        cleared = 0
        if namespace is None:
            for ns in self._namespaces:
                cleared += len(self._namespaces[ns])
                self._namespaces[ns] = {}
        else:
            self._validate_namespace(namespace)
            cleared = len(self._namespaces[namespace])
            self._namespaces[namespace] = {}
        self._stats["clears"] += 1
        return cleared

    # ── Queries ──

    def count(self, namespace: str) -> int:
        """Count records in a namespace."""
        self._validate_namespace(namespace)
        return len(self._namespaces[namespace])

    def total_count(self) -> int:
        """Total records across all namespaces."""
        return sum(len(v) for v in self._namespaces.values())

    def stats(self) -> Dict[str, int]:
        """Return storage operation statistics."""
        return {
            **self._stats,
            "total_records": self.total_count(),
            "namespace": self.NAMESPACE,
        }

    def list_namespaces(self) -> List[str]:
        """List all available namespace names."""
        return list(self._namespaces.keys())

    def export_all(self) -> Dict[str, Dict[str, Any]]:
        """Export all namespaces as a nested dict.

        Returns:
            Dict of namespace -> {record_id -> record}
        """
        return {
            ns: dict(records) for ns, records in self._namespaces.items()
        }

    # ── Internal ──

    def _validate_namespace(self, namespace: str) -> None:
        """Validate that namespace is one of the allowed namespaces."""
        if namespace not in self._namespaces:
            raise ValueError(
                f"Invalid namespace '{namespace}'. "
                f"Must be one of: {sorted(self._namespaces.keys())}"
            )

    def __repr__(self) -> str:
        return (
            f"ShadowStorage(ns={self.NAMESPACE}, "
            f"records={self.total_count()}, "
            f"stores={self._stats['stores']}, "
            f"loads={self._stats['loads']})"
        )