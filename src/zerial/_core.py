import attr


def deztructure(inst, _dict_factory=dict):
    fields = attr.fields(inst.__class__)
    ret = _dict_factory()
    for field in fields:
        value = getattr(inst, field.name)
        if attr.has(field.type):
            ret[field.name] = deztructure(value, _dict_factory)
        else:
            ret[field.name] = value
    return ret


def reztructure(klass, mapping):
    # TODO: implement efficiency compat for py2 without six if possible
    fields = attr.fields(klass)
    kwargs = {}
    for field in fields:
        data = mapping[field.name]
        if attr.has(field.type):
            kwargs[field.name] = reztructure(field.type, data)
        else:
            kwargs[field.name] = data
    return klass(**kwargs)
