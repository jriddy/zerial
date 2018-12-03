from abc import ABCMeta, abstractmethod
from enum import Enum, unique
from functools import partial
from typing import (
    Type, Generic, Callable, TypeVar, Iterable, MutableSequence, Sequence,
    cast, Union, Tuple,
)

import attr

from ._compat import isconcretetype, with_metaclass


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


class _Ztype(with_metaclass(ABCMeta)):
    """ztype interface

    Despite the name it is not an actual type, but a transfomer object.  It is
    meant to be stored as metadata on record types and extracted to use in
    structuring operations.
    """
    @abstractmethod
    def destruct(self, inst, ztr):
        """Unstructure inst into a mapping.

        The Ztructurer doing the destructuring is passed for its options and to
        permit further recursive descent if necessary.

        Works with the Ztructurer to take apart more complex types.
        """

    @abstractmethod
    def restruct(self, mapping, ztr):
        """Structure the mapping into the appropriate type.

        The Ztructurer doing the rebuilding is passed for its options and to
        permit recursive rebuilding if needed.

        Works with Ztructurer to rebuild more complext types.
        """


@attr.s
class Zequence(_Ztype, Generic[T, R, D]):
    item_type = attr.ib()  # type: Type[T]
    restructure_factory = attr.ib(
        default=cast(Callable[[I_T], R], list)
    )  # type: Callable[[I_T], R]
    destructure_factory = attr.ib(
        default=cast(Callable[[I_T], D], list)
    )  # type: Callable[[I_T], D]
    apparent_type = attr.ib()  # type: Type[T]

    @apparent_type.default
    def default_apparent_type(self):
        return MutableSequence[self.item_type]

    def destruct(self, inst, ztr):
        if ztr.can_structure(self.item_type):
            dez = ztr.destructure
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

    def destruct(self, inst, ztr):
        ident = lambda x: x
        dez = ztr.destructure if ztr.can_structure(self.val_type) else ident
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


def _check_convert_zariant_types(types):
    """Do the type validation before we even get anywhere.

    Nothing else in Zariant makes sense without sound types.
    """
    types = tuple(types)
    if len(types) < 2:
        raise ValueError("Zariant requires at least 2 types.")
    for t in types:
        if not isconcretetype(t):
            raise TypeError(
                "Zariant requires concrete types, %s is not" % (t,)
            )
    return types


@attr.s
class Zariant(_Ztype):
    types = attr.ib(
        type=Iterable[Type],
        converter=_check_convert_zariant_types,
    )

    _name = attr.ib(type=str)

    @_name.default
    def _gen_name(self):
        return 'Zenum___' + '__'.join(t.__name__ for t in self.types)

    _enum = attr.ib(type=Enum)

    @_enum.default
    def _make_enum(self):
        types = self.types
        pairs = ((t.__name__, t) for t in types)
        return unique(Enum(self.name, pairs))

    @property
    def name(self):
        return self._name

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
        type_name = data[ztr.get_metakey('type')]
        type_ = self._enum[type_name].value
        if ztr.can_structure(type_):
            return ztr.restructure(type_, data)
        else:
            # TODO: should we pass to type_ here?
            return data[ztr.get_metakey('value')]

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
