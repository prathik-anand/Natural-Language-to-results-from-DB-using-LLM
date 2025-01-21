from functools import lru_cache

@lru_cache(maxsize=1)
def cache_data(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
