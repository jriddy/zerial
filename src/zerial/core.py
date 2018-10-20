import attr


def deztructure(inst, _dict_factory=dict):
    fields = attr.fields(inst.__class__)
    ret = _dict_factory()
    for field in fields:
        value = getattr(inst, field.name)
        if attr.has(value.__class__):
            ret[field.name] = deztructure(value, _dict_factory)
        else:
            ret[field.name] = value
    return ret


def reztructure(typ, dct):
    return typ(**dct)
