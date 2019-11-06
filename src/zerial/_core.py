from operator import attrgetter

import attr

from ._base import Ztype as _Ztype


DEFAULT_PASSTHRUS = (
    # basically defined by what JSON understands, minus null==None
    bool, int, float, str,
)


@attr.s
class Ztructurer(object):
    dict_factory = attr.ib(default=dict)
    metachar = attr.ib(type=str, default='%')
    permitted_passthrus = attr.ib(type=tuple, default=DEFAULT_PASSTHRUS)
    is_serializable_field = attr.ib(default=attrgetter('init'))
    encoders = attr.ib(factory=dict)
    _can_structure = attr.ib(default=attr.has)

    def get_metakey(self, key):
        # type (str) -> str
        return self.metachar + key

    def destructure(self, inst, type=None):
        if isinstance(type, _Ztype):
            return type.destruct(inst, self)
        encoder = self.get_encoder(type)
        if encoder is not None:
            return encoder.encode(inst, self)
        fields = attr.fields(inst.__class__ if type is None else type)
        ret = self.dict_factory()
        for field in filter(self.is_serializable_field, fields):
            name = field.name
            key = name.lstrip('_')
            value = getattr(inst, name)
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                ret[key] = ztype.destruct(value, self)
            elif self.can_structure(field.type):
                ret[key] = self.destructure(value, field.type)
            elif self.can_pass_thru(value):
                ret[key] = value
            else:
                raise TypeError("cannot destructure {!r}".format(value))
        return ret

    def restructure(self, type, mapping):
        if isinstance(type, _Ztype):
            return type.restruct(mapping, self)
        encoder = self.get_encoder(type)
        if encoder is not None:
            return encoder.decode(mapping, self)
        fields = attr.fields(type)
        kwargs = {}
        for field in filter(self.is_serializable_field, fields):
            name = field.name
            key = name.lstrip('_')
            # defer asserting the key's existence until the constructing the object
            if key not in mapping:
                continue
            data = mapping[key]
            ztype = field.metadata.get('zerial.ztype')
            if ztype is not None:
                kwargs[key] = ztype.restruct(data, self)
            elif self.can_structure(field.type):
                kwargs[key] = self.restructure(field.type, data)
            else:
                kwargs[key] = data
        return type(**kwargs)

    def can_pass_thru(self, val):
        return isinstance(val, self.permitted_passthrus)

    def get_encoder(self, type):
        return self.encoders.get(type)

    def can_encode(self, type):
        return type in self.encoders

    def can_structure(self, tobj):
        tobj = tobj if isinstance(tobj, type) else tobj.__class__
        return self._can_structure(tobj) or self.can_encode(tobj)

    def record(self, cls):
        # type: (type) -> type
        """
        Decorator to indicate that a class is serializable

        Currently does nothing special, but in the future it may be used to
        add automated features, and could potentially become required to
        serialize objects in certain contexts.
        """
        cls.__zerial_record__ = True
        return cls
