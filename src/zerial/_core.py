import attr


@attr.s
class Ztructurer(object):
    dict_factory = attr.ib(default=dict)
    metachar = attr.ib(type=str, default='%')
    permitted_passthrus = attr.ib(type=tuple, default=(
        # basically defined by what JSON understands, minus null==None
        bool, int, float, str,
    ))
    can_structure = attr.ib(default=attr.has)

    def get_metakey(self, key):
        # type (str) -> str
        return self.metachar + key

    def destructure(self, inst):
        fields = attr.fields(inst.__class__)
        ret = self.dict_factory()
        for field in fields:
            name = field.name
            key = name.lstrip('_')
            value = getattr(inst, name)
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                ret[key] = ztype.destruct(value, self)
            elif attr.has(field.type):
                ret[key] = self.destructure(value)
            elif self.can_pass_thru(value):
                ret[key] = value
            else:
                raise TypeError("cannot destructure {!r}".format(value))
        return ret

    def restructure(self, klass, mapping):
        fields = attr.fields(klass)
        kwargs = {}
        for field in fields:
            name = field.name
            key = name.lstrip('_')
            data = mapping[key]
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                kwargs[key] = ztype.restruct(data, self)
            elif attr.has(field.type):
                kwargs[key] = self.restructure(field.type, data)
            else:
                kwargs[key] = data
        return klass(**kwargs)

    def can_pass_thru(self, val):
        return isinstance(val, self.permitted_passthrus)
