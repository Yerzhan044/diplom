"""Caching layer for SHAP explanations and predictions."""

import hashlib
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class ExplanationCache:
    """Simple in-memory cache for SHAP explanations."""

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0

    def _hash_features(self, features_dict: dict[str, float]) -> str:
        """Create hash of feature dict for cache key."""
        # Round float values to 4 decimals to group similar transactions
        rounded = {k: round(v, 4) for k, v in features_dict.items()}
        json_str = json.dumps(rounded, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    def get(self, features_dict: dict[str, float]) -> Optional[dict[str, Any]]:
        """Get cached explanation if available."""
        key = self._hash_features(features_dict)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, features_dict: dict[str, float], explanation: dict[str, Any]) -> None:
        """Cache an explanation."""
        if len(self.cache) >= self.max_size:
            # Simple FIFO eviction
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        key = self._hash_features(features_dict)
        self.cache[key] = explanation

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "total_requests": total,
            "hit_rate": f"{hit_rate:.1%}",
            "cache_size": len(self.cache),
            "max_size": self.max_size,
        }


class PredictionCache:
    """Cache for model predictions."""

    def __init__(self, max_size: int = 5000):
        self.cache = {}
        self.max_size = max_size

    def _hash_features(self, features_dict: dict[str, float]) -> str:
        """Create hash of feature dict for cache key."""
        rounded = {k: round(v, 4) for k, v in features_dict.items()}
        json_str = json.dumps(rounded, sort_keys=True)
        return hashlib.md5(json_str.encode()).hexdigest()

    def get(self, features_dict: dict[str, float]) -> Optional[dict[str, float]]:
        """Get cached prediction."""
        key = self._hash_features(features_dict)
        return self.cache.get(key)

    def set(
        self,
        features_dict: dict[str, float],
        fraud_prob: float,
        anomaly_score: float,
    ) -> None:
        """Cache a prediction."""
        if len(self.cache) >= self.max_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]

        key = self._hash_features(features_dict)
        self.cache[key] = {
            "fraud_probability": fraud_prob,
            "anomaly_score": anomaly_score,
        }

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
