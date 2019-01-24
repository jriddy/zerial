from enum import Enum, unique
from functools import partial
from operator import methodcaller
from typing import (
    Type, Generic, Callable, TypeVar, Iterable, MutableSequence,
    Sequence as TSequence,
    cast, Union, Tuple, MutableMapping,
)

import attr

from ._base import Ztype as _Ztype
from ._compat import isconcretetype, Mapping as TMapping


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
R = TypeVar('R', bound=TSequence)
D = TypeVar('D', bound=TSequence)
K = TypeVar('K')
V = TypeVar('V')
I_T = Iterable[T]
I_KV = Iterable[Tuple[K, V]]


@attr.s
class Sequence(_Ztype, Generic[T, R, D]):
    """Metadata type for a sequence of items.

    Handles any version of N number of items of type T.  Works for sets,
    tuples, lists, and anything else that follows that interface.

    :attribute item_type: The type of the object contained in this sequence.
        Note that this can itself be another complex object or another Ztype,
        so these data types can be arbitrarily nested.

    :attribute restructure_factory: The callable that will convert a stored
        sequence into a live data type.  Basically, the function that can
        rebuild your data into the collection type you want.

    :attribute destructure_factory: The callable that will convert a live
        sequence into storage data.  Normally this will always be list,
        unless your serialization format supports other sequence types.

    :attribute apparent_type:  To be deprecated
    """
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
class Mapping(_Ztype, Generic[K, V, R, D]):
    """Ztype wrapper for a simple mapping/dict

    Since many serialization formats require that keys for mappings be strings,
    we require that the key_type be convertible to-and-from string.  This
    limits us to pretty primitive types, like int and str.

    :attribute key_type: The type of the keys of the mapping.  Currently only
        supports types that can do a straight-forward one-to-one convertion to
        and from ``str``.

    :attribute val_type: The type of the values of the mapping.  Can be any
        type that will can be serialized, including other :class:`Ztype`
        objects, allowing arbirarily complex value types.

    :attribute restructure_factory:  The container type that will be used to
        rebuild your data type upon being restructured.  It will be called with
        an iterable of key-value pairs. The default is dict, but if you want,
        say, a :class:`collections.defaultdict` to come out with a default
        function of ``int``, you could give this::

            @zerial.record
            @attr.s
            class MyRecord:
                my_field = attr.ib(
                    type=typing.Mapping[str, int],
                    metadata=zerial.data(zerial.Mapping(
                        str, int, partial(defaultdict, int)
                    )),
                )

        This will result in ``my_field`` being restructured ready for you to do
        all the fun ``defaultdict`` stuff you've always wanted to do like
        ``my_record.my_field[arbitrary_key] += 1``, because ``zerial`` ensures
        that it gets restructured that way.

    :attribute destructure_factory:  The container type that will be used to
        take apart your data to destructure it.  Can be useful if your mapping
        is ordered, in which case you'd want to save it as a ``list`` to
        preserve the order even in a serialized dict.  This feature is
        unstable and may be replaced by something more sophisticated in the
        future.

    :attribute extract_pairs:  Function to extract item pairs from the object
        created by ``destructure_factory``.  By default, this calls
        ``.items()`` on the object it receives, but if you were to destructure
        into a ``list``, you'll need to pass ``None`` here (which is converted
        to the identity function ``lambda x: x``) since a list of pairs is
        already, well, a list of pairs.  This feature is unstable and may be
        replaced by something better in the future.
    """
    key_type = attr.ib(type=Type[K])
    val_type = attr.ib(type=Type[V])
    restructure_factory = attr.ib(
        default=cast(Callable[[I_KV], R], dict)
    )  # type: Callable[[I_KV], R]
    destructure_factory = attr.ib(
        default=cast(Callable[[I_KV], D], dict)
    )  # type: Callable[[I_KV], D]
    extract_pairs = attr.ib(
        default=methodcaller('items'),
        converter=lambda f: (lambda x: x) if f is None else f,
    )
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
        ex_pairs = self.extract_pairs
        return self.restructure_factory(
            (Key(k), valf(Val, v)) for k, v in ex_pairs(mapping)
        )


@attr.s
class Serializer(_Ztype, Generic[T, U]):
    """When you just need a serializer that goes forward and back.

    :attribute to_outer: Function that destructures the data.
    :attribute to_inner: Function that restructures the data.

    If the other metadata types fail, or there are obvious standard string
    representations of your data type (like in dates), you can just use a
    :class:`Serializer` to take care of it for you::

        import datetime

        @zerial.record
        @attr.s
        class ImportantDate:
            name = attr.ib(type=str)
            date = attr.ib(
                type=datetime.date,
                metadata=zerial.data(zerial.Serializer(
                    lambda d: d.isoformat(),
                    lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(),
                )),
            )

    It doesn't necessarily have to be a string either.  If your mapping variant
    is too complex for :class:`Mapping`, then you could use this class as a
    last resort for defining a method of destructuring it.
    """
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
    types = types.items() if isinstance(types, TMapping) else tuple(types)
    type_records = tuple(map(_ZariantRecord.from_type_or_tuple, types))
    if len(type_records) < 2:
        raise ValueError("Zariant requires at least 2 types.")
    return type_records


@attr.s
class Variant(_Ztype):
    """Variant that allows multiple types to occupy the same attribute slot.

    This is an implementation of a sum type (called enums or variants,
    depending on the source) for serialization.  It allows multiple types to be
    saved in the same slot, and deserialized intelligently into the correct
    type.  It accomplishes this by storing a name corresponding to the type
    along with the type information.

    :attribute _type_records: Iterable of types, or a mapping of names to
        types.  The types should be concrete types, in the sense that they can
        instantiate a real object of their class from provided data.  They are
        treated as invariant.  If you have multiple subclasses of a type, they
        must all be specified here.  The ``Variant`` has to be able to store
        the type in the destructured data and consistently map it to the
        desired runtime type in the restuctured model, so it needs a full
        accounting of which types are available to it at definition time.  If
        passed a mapping, the keys are taken as the type names.  If passed a
        plain iterable, the type names are taken from the ``__name__``
        attribute of the class.  Collisions are invalid, so if you have two
        types with the same ``__name__``, use a mapping to give them unique
        names in this context.

    :attribute default: Default type to use if no type information is found in
        the destructured data.  This permits previously non-variant field to
        become variants without invalidating previously saved data.
    """
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


# TODO: remove renames when code is audited
Zequence = Sequence
Zapping = Mapping
Zerializer = Serializer
Zariant = Variant
