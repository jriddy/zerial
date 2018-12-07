from enum import Enum, unique
from functools import partial
from typing import (
    Type, Generic, Callable, TypeVar, Iterable, MutableSequence, Sequence,
    cast, Union, Tuple, MutableMapping
)

import attr

from ._base import Ztype as _Ztype
from ._compat import isconcretetype, Mapping


def zdata(ztype):
    if isinstance(ztype, _Ztype):
        pass
    elif isinstance(ztype, type):
        ztype = Zendthru(ztype)
    else:
        raise TypeError("{} is not a type or valid transformer".format(ztype))
    return {'zerial.ztype': ztype}


T = TypeVar('T')
U = TypeVar('U')
R = TypeVar('R', bound=Sequence)
D = TypeVar('D', bound=Sequence)
K = TypeVar('K')
V = TypeVar('V')
I_T = Iterable[T]
I_KV = Iterable[Tuple[K, V]]


@attr.s
class Zequence(_Ztype, Generic[T, R, D]):
    item_type = attr.ib()  # type: Union[Type[T], _Ztype]
    restructure_factory = attr.ib(
        default=cast(Callable[[I_T], R], list)
    )  # type: Callable[[I_T], R]
    destructure_factory = attr.ib(
        default=cast(Callable[[I_T], D], list)
    )  # type: Callable[[I_T], D]
    apparent_type = attr.ib()  # type: Type[T]

    @apparent_type.default
    def default_apparent_type(self):
        # TODO: remove apparent types maybe?  or ship our own mypy plugin
        itype = self.item_type
        if isinstance(itype, _Ztype):
            itype = itype.apparent_type
        return MutableSequence[itype]

    def destruct(self, inst, ztr):
        if ztr.can_structure(self.item_type):
            dez = partial(ztr.destructure, type=self.item_type)
            return self.destructure_factory(dez(x) for x in inst)
        else:
            # TODO: are there conditions when we can just do `return inst`?
            return self.destructure_factory(inst)

    def restruct(self, data, ztr):
        if ztr.can_structure(self.item_type):
            rez = partial(ztr.restructure, self.item_type)
            return self.restructure_factory(rez(x) for x in data)
        else:
            return self.restructure_factory(data)


@attr.s
class Zapping(_Ztype, Generic[K, V, R, D]):
    """Ztype wrapper for a simple mapping/dict

    Since many serialization formats require that keys for mappings be strings,
    we require that the key_type be convertible to-and-from string.  This
    limits us to pretty primitive types, like int and str.
    """
    key_type = attr.ib(type=Type[K])
    val_type = attr.ib(type=Type[V])
    restructure_factory = attr.ib(
        default=cast(Callable[[I_KV], R], dict)
    )  # type: Callable[[I_KV], R]
    destructure_factory = attr.ib(
        default=cast(Callable[[I_KV], D], dict)
    )  # type: Callable[[I_KV], D]
    apparent_type = attr.ib(default=MutableMapping)

    def destruct(self, inst, ztr):
        if ztr.can_structure(self.val_type):
            dez = partial(ztr.destructure, type=self.val_type)
        else:
            dez = lambda x: x
        return self.destructure_factory(
            (str(k), dez(v)) for k, v in inst.items()
        )

    def restruct(self, mapping, ztr):
        Key, Val = self.key_type, self.val_type
        valf = (ztr.restructure
                if ztr.can_structure(Val) else
                lambda _, x: Val(x))
        return self.restructure_factory(
            (Key(k), valf(Val, v)) for k, v in mapping.items()
        )


@attr.s
class Zerializer(_Ztype, Generic[T, U]):
    """When you just need a serializer that goes forward and back."""
    to_outer = attr.ib(type=Callable[[T], U])
    to_inner = attr.ib(type=Callable[[U], T])

    def destruct(self, inst, _):
        return self.to_outer(inst)

    def restruct(self, data, _):
        return self.to_inner(data)


@attr.s(slots=True)
class _ZariantRecord(object):
    type = attr.ib(type=type)
    name = attr.ib(type=str)

    @name.default
    def _default_name(self):
        return self.type.__name__

    @type.validator
    def _validate_type(self, _, type_):
        if not isconcretetype(type_):
            raise TypeError(
                "Zariant requires concrete types, %s is not" % (type_,)
            )

    @classmethod
    def from_type_or_tuple(cls, tot):
        if isinstance(tot, type):
            return cls(tot)
        else:
            name, type_ = tot
            return cls(type_, name)


def _check_convert_zariant_types(types):
    """Do the type validation before we even get anywhere.

    Nothing else in Zariant makes sense without sound types.
    """
    types = types.items() if isinstance(types, Mapping) else tuple(types)
    type_records = tuple(map(_ZariantRecord.from_type_or_tuple, types))
    if len(type_records) < 2:
        raise ValueError("Zariant requires at least 2 types.")
    return type_records


@attr.s
class Zariant(_Ztype):
    _type_records = attr.ib(
        type=Iterable[_ZariantRecord],
        converter=_check_convert_zariant_types,
    )
    NO_DEFAULT = object()
    default = attr.ib(default=NO_DEFAULT)

    _name = attr.ib(type=str)

    @_name.default
    def _gen_name(self):
        return 'Zenum___' + '__'.join(t.name for t in self._type_records)

    _enum = attr.ib(type=Enum)

    @_enum.default
    def _make_enum(self):
        pairs = ((t.name, t.type) for t in self._type_records)
        return unique(Enum(self.name, pairs))

    @default.validator
    def _convert_default(self, _, value):
        if value is self.NO_DEFAULT:
            return
        enum = self._enum
        if isinstance(value, enum):
            return
        elif isinstance(value, str):
            self.default = enum[value]
        elif isinstance(value, type):
            self.default = enum(value)
        else:
            raise TypeError("not a valid type for default: %r" % (value,))

    @property
    def name(self):
        return self._name

    @property
    def types(self):
        return tuple(t.type for t in self._type_records)

    def _force_type(self, value):
        if not isinstance(value, self.types):
            raise TypeError("Value not valid for this zariant %s" % (value,))

    def destruct(self, inst, ztr):
        self._force_type(inst)  # is this necessary in light of the enum?
        entry = self._enum(type(inst))
        if ztr.can_structure(entry.value):
            data = ztr.destructure(inst)
            # TODO: dict_factory could produce immutables...think about it
            data[ztr.get_metakey('type')] = entry.name
            return data
        else:
            return ztr.dict_factory([
                (ztr.get_metakey('type'), entry.name),
                (ztr.get_metakey('value'), inst),
            ])

    def restruct(self, data, ztr):
        try:
            type_name = data[ztr.get_metakey('type')]
        except (TypeError, KeyError):
            if self.default is self.NO_DEFAULT:
                raise
            type_ = self.default.value
            in_dict = False
        else:
            type_ = self._enum[type_name].value
            in_dict = True
        if ztr.can_structure(type_):
            return ztr.restructure(type_, data)
        elif in_dict:
            # TODO: should we pass to type_ here?
            return data[ztr.get_metakey('value')]
        else:
            return data

    @property
    def apparent_type(self):
        return Union.__getitem__(self.types)


@attr.s
class Zendthru(_Ztype):
    pass_type = attr.ib(type=type)

    def _check_type(self, inst):
        if not isinstance(inst, self.pass_type):
            raise TypeError(
                '{!r} is an instance of {!r}, not {!r}'.format(
                    inst, type(inst), self.pass_type,
                )
            )

    def destruct(self, inst, _ztr):
        self._check_type(inst)
        return inst

    def restruct(self, data, _ztr):
        self._check_type(data)
        return data
