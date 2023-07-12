from django.core.cache import cache

DEFAULT_EXPIRY_TIME = 30 * 60
CACHE_KEY_LENGTH_MAX_SIZE = 5000

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

CACHE_KEY_CATEGORY_INFOS_DICT = {
    'cache_key_converter': lambda cache_prefix: cache_prefix,
    'cache_prefix': 'book.category.infos',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_KEY_AUTHOR_INFOS_DICT = {
    'cache_key_converter': lambda cache_prefix: cache_prefix,
    'cache_prefix': 'book.author.infos',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_KEY_PUBLISHER_INFOS_DICT = {
    'cache_key_converter': lambda cache_prefix: cache_prefix,
    'cache_prefix': 'book.publisher.infos',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_KEY_BOOK_INFOS = {
    'cache_key_converter': lambda cache_prefix, book_id: cache_prefix % book_id,
    'cache_prefix': 'book.infos.id.%s',
    'expiry_time': DEFAULT_EXPIRY_TIME
}

CACHE_KEY_CLUB_BOOK_INFOS = {
    'cache_key_converter': lambda cache_prefix, club_book_id: cache_prefix % club_book_id,
    'cache_prefix': 'club_book.id.%s',
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

# input: must be a list follow by some args
# output: must be a dict
def combine_key_cache_data(cache_key_converter, cache_prefix, expiry_time=DEFAULT_EXPIRY_TIME):
    def _cache_data(func):
        def _func(keys, *args, **kwargs):
            if not keys:
                return {}
            keys = list(set(keys))
            force_query = kwargs.get("force_query", force_query_default)
            result_data = {}
            if not force_query:
                cache_key_map = {cache_key_converter(cache_prefix, key, *args): key for key in keys}
                cache_key_list = cache_key_map.keys()
                length = len(cache_key_list)
                cached_data_dict = {}
                for i in range(0, length, CACHE_KEY_LENGTH_MAX_SIZE):
                    cache_keys = list(cache_key_list)[i:i + CACHE_KEY_LENGTH_MAX_SIZE]
                    cached_data_dict.update(cache.get_many(cache_keys))

                result_data = {cache_key_map[cached_key]: cached_data for cached_key, cached_data in
                               cached_data_dict.items()}
                keys = list(set(keys) - set(result_data.keys()))
            if keys:
                response_data = func(keys, *args)
                if response_data:
                    data_to_cache = {cache_key_converter(cache_prefix, key, *args): data for key, data in
                                     response_data.items()}
                    cache.set_many(data_to_cache, expiry_time)
                return {**result_data, **response_data}
            else:
                return result_data

        return _func

    return _cache_data
