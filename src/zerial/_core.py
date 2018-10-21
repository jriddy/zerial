import attr


@attr.s
class Ztructurer(object):
    dict_factory = attr.ib(default=dict)

    def deztructure(self, inst):
        fields = attr.fields(inst.__class__)
        ret = self.dict_factory()
        for field in fields:
            value = getattr(inst, field.name)
            if attr.has(field.type):
                ret[field.name] = self.deztructure(value)
            else:
                ret[field.name] = value
        return ret


    def reztructure(self, klass, mapping):
        # TODO: implement efficiency compat for py2 without six if possible
        fields = attr.fields(klass)
        kwargs = {}
        for field in fields:
            data = mapping[field.name]
            if attr.has(field.type):
                kwargs[field.name] = self.reztructure(field.type, data)
            else:
                kwargs[field.name] = data
        return klass(**kwargs)
