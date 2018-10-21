import attr


@attr.s
class Ztructurer(object):
    dict_factory = attr.ib(default=dict)

    def can_structure(self, inst):
        return attr.has(inst)

    def destructure(self, inst):
        fields = attr.fields(inst.__class__)
        ret = self.dict_factory()
        for field in fields:
            name = field.name
            value = getattr(inst, name)
            ztype = field.metadata.get('zerial', {}).get('ztype')
            if ztype is not None:
                ret[name] = ztype.destruct(value, self)
            elif attr.has(field.type):
                ret[name] = self.destructure(value)
            else:
                ret[name] = value
        return ret

    def restructure(self, klass, mapping):
        fields = attr.fields(klass)
        kwargs = {}
        for field in fields:
            name = field.name
            data = mapping[name]
            ztype = field.metadata.get('zerial', {}).get('ztype')
            if ztype is not None:
                kwargs[name] = ztype.restruct(data, self)
            elif attr.has(field.type):
                kwargs[name] = self.restructure(field.type, data)
            else:
                kwargs[name] = data
        return klass(**kwargs)
