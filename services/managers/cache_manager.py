DEFAULT_EXPIRY_TIME = 10 * 60


force_query_default = False

# def simple_cache_data(cache_key_converter, cache_prefix, expiry_time=DEFAULT_EXPIRY_TIME, cache_name='default'):
#     def _cache_data(func):
#         def _func(*args, **kwargs):
#             cache_key = cache_key_converter(cache_prefix, *args)
#             data = cache.get_cache(cache_name).get(cache_key)
#             force_query = kwargs.get("force_query", force_query_default)
#             if force_query or data is None:
#                 data = func(*args)
#                 if data:
#                     cache.get_cache(cache_name).set(cache_key, data, expiry_time)
#             return data
#
#         return _func
#
#     return _cache_data
