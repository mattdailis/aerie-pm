def opt(*keys, default=None):
    def _(obj):
        res = obj
        for key in keys:
            if type(key) == str:
                func = lambda x: x[key]
            else:
                func = key
            try:
                res = func(res)
            except (KeyError, TypeError):
                return default
        return res

    return _
