from functools import partial
from typing import (
    Generic, Callable, TypeVar, Iterable, MutableSequence, Sequence, cast
)

import attr


def zdata(ztype):
    # TODO: we should do something more intelligent with real types here
    if not isinstance(ztype, (_Ztype, type)):
        raise TypeError("{} is not a type or valid transformer".format(ztype))
    return {'zerial': {
        'ztype': ztype,
    }}


T = TypeVar('T')
R = TypeVar('R', bound=Sequence)
D = TypeVar('D', bound=Sequence)
I_T = Iterable[T]


class _Ztype(object):
    """ztype interface

    Don't put anything concrete in it please.

    Despite the name it is not an actual type, but a transfomer object.
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
            return self.destructure_factory(
                dez(x) for x in inst
            )
        else:
            # TODO: are there conditions when we can just do `return inst`?
            return self.destructure_factory(inst)

    def restruct(self, data, ztr):
        if ztr.can_structure(self.item_type):
            rez = partial(ztr.restructure, self.item_type)
            return self.restructure_factory(
                rez(x) for x in data,
            )
        else:
            return self.restructure_factory(data)
