from functools import partial
from typing import (
    Generic, Callable, TypeVar, Type, Iterable, MutableSequence, Sequence
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
R = TypeVar('R', bound=Sequence[T])
D = TypeVar('D', bound=Sequence[T])
I_T = Iterable[T]


class _Ztype(object):
    """ztype interface

    Don't put anything concrete in it please.

    Despite the name it is not an actual type, but a transfomer object.
    """


@attr.s
class Zequence(_Ztype, Generic[T, R, D]):
    item_type = attr.ib(type=Type[T])
    reztructure_factory = attr.ib(type=Callable[[I_T], R], default=list)
    deztructure_factory = attr.ib(type=Callable[[I_T], D], default=list)
    apparent_type = attr.ib(type=Type[T])

    @apparent_type.default
    def default_apparent_type(self):
        return MutableSequence[self.item_type]

    def deztruct(self, inst, ztr):
        if ztr.can_ztructure(self.item_type):
            dez = ztr.deztructure
            return self.deztructure_factory(
                dez(x) for x in inst
            )
        else:
            # TODO: are there conditions when we can just do `return inst`?
            return self.deztructure_factory(inst)

    def reztruct(self, data, ztr):
        if ztr.can_ztructure(self.item_type):
            rez = partial(ztr.reztructure, self.item_type)
            return self.reztructure_factory(
                rez(x) for x in data,
            )
        else:
            return self.reztructure_factory(data)
