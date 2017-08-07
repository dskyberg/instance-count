def getparam(target, param, default=None, delete=False):
    if target is None:
        return default
    if not isinstance(target, dict):
        raise ValueError('getparam: target must be a dict')
    if param in target:
        value = target[param]
        if delete:
            del target[param]
        return value
    else:
        return default
