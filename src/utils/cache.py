"""
Simple LRU cache implementation with TTL support.
"""
import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)


class TTLCache:
    """
    LRU Cache with Time-To-Live (TTL) support.
    Thread-safe implementation.
    """

    def __init__(self, maxsize: int = 128, ttl: float = 3600):
        """
        Initialize the cache.

        Args:
            maxsize: Maximum number of items in the cache
            ttl: Time-to-live for items in seconds (default: 1 hour)
        """
        self.maxsize = maxsize
        self.ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[Any, float] = {}
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0

    def _is_expired(self, key: Any) -> bool:
        """Check if a cache entry has expired."""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl

    def _cleanup_expired(self):
        """Remove expired entries from cache."""
        now = time.time()
        expired_keys = [
            key for key, timestamp in self.timestamps.items()
            if now - timestamp > self.ttl
        ]
        for key in expired_keys:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)

    def get(self, key: Any) -> Optional[Any]:
        """
        Get an item from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        with self.lock:
            # Cleanup expired entries occasionally
            if len(self.cache) > self.maxsize // 2:
                self._cleanup_expired()

            if key in self.cache and not self._is_expired(key):
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                self.hits += 1
                return self.cache[key]
            else:
                # Remove expired entry if present
                self.cache.pop(key, None)
                self.timestamps.pop(key, None)
                self.misses += 1
                return None

    def set(self, key: Any, value: Any):
        """
        Set an item in the cache.

        Args:
            key: Cache key
            value: Value to cache
        """
        with self.lock:
            # If key already exists, remove it first
            if key in self.cache:
                self.cache.pop(key)
            # If cache is full, remove least recently used item
            elif len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)

            self.cache[key] = value
            self.timestamps[key] = time.time()
            # Move to end (most recently used)
            self.cache.move_to_end(key)

    def delete(self, key: Any):
        """
        Delete an item from the cache.

        Args:
            key: Cache key
        """
        with self.lock:
            self.cache.pop(key, None)
            self.timestamps.pop(key, None)

    def clear(self):
        """Clear all items from the cache."""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()
            self.hits = 0
            self.misses = 0

    def size(self) -> int:
        """Get current cache size."""
        with self.lock:
            # Cleanup expired entries before returning size
            self._cleanup_expired()
            return len(self.cache)

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = self.hits / total_requests if total_requests > 0 else 0
            return {
                "size": self.size(),
                "maxsize": self.maxsize,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": hit_rate
            }


# Global cache instance for validation results
validation_cache = TTLCache(maxsize=256, ttl=1800)  # 256 items, 30 minutes TTL