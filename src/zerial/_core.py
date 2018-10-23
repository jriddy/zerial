import attr


@attr.s
class Ztructurer(object):
    dict_factory = attr.ib(default=dict)
    metachar = attr.ib(type=str, default='%')
    permitted_passthrus = attr.ib(type=tuple, default=(
        # basically defined by what JSON understands, minus null==None
        bool, int, float, str,
    ))

    def can_structure(self, inst):
        return attr.has(inst)

    def get_metakey(self, key):
        # type (str) -> str
        return self.metachar + key

    def destructure(self, inst):
        fields = attr.fields(inst.__class__)
        ret = self.dict_factory()
        for field in fields:
            name = field.name
            value = getattr(inst, name)
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                ret[name] = ztype.destruct(value, self)
            elif attr.has(field.type):
                ret[name] = self.destructure(value)
            elif self.can_pass_thru(value):
                ret[name] = value
            else:
                raise TypeError("cannot destructure {!r}".format(value))
        return ret

    def restructure(self, klass, mapping):
        fields = attr.fields(klass)
        kwargs = {}
        for field in fields:
            name = field.name
            data = mapping[name]
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                kwargs[name] = ztype.restruct(data, self)
            elif attr.has(field.type):
                kwargs[name] = self.restructure(field.type, data)
            else:
                kwargs[name] = data
        return klass(**kwargs)

    def can_pass_thru(self, val):
        return isinstance(val, self.permitted_passthrus)
