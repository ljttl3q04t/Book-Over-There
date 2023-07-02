from django.core.cache import cache

DEFAULT_EXPIRY_TIME = 10 * 60

force_query_default = False

CACHE_KEY_MEMBER_CLUB = {
    'cache_key_converter': lambda cache_prefix, club: cache_prefix % club.id,
    'cache_prefix': 'member.infos.club.%s',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_KEY_MEMBER_INFOS = {
    'cache_key_converter': lambda cache_prefix: cache_prefix,
    'cache_prefix': 'member.infos.club.%s',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_CLUB_GET_INFOS_DICT = {
    'cache_key_converter': lambda cache_prefix: cache_prefix,
    'cache_prefix': 'club.infos',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

def simple_cache_data(cache_key_converter, cache_prefix, expiry_time=DEFAULT_EXPIRY_TIME):
    def _cache_data(func):
        def _func(*args, **kwargs):
            cache_key = cache_key_converter(cache_prefix, *args)
            data = cache.get(cache_key)
            force_query = kwargs.get("force_query", force_query_default)
            if force_query or data is None:
                data = func(*args)
                if data:
                    cache.set(cache_key, data, expiry_time)
            return data

        return _func

    return _cache_data
