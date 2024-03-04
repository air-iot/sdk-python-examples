from cacheout import Cache
from cacheout.lfu import LFUCache
from cacheout.lru import LRUCache
from cacheout.mru import MRUCache


def create_cache(max_size: int = 1000, policy: str = "lru", ttl: int = 3600) -> Cache:
    if policy == "lru":
        return LRUCache(maxsize=max_size, ttl=ttl)

    if policy == "lfu":
        return LFUCache(maxsize=max_size, ttl=ttl)

    if policy == "mru":
        return MRUCache(maxsize=max_size, ttl=ttl)

    raise Exception("Unsupported evict policy: {}".format(policy))
