from typing import (
    Generic, Callable, TypeVar, Type, Iterable, MutableSequence, Sequence
)

import attr


def zdata(ztype):
    # TODO: we should do something more intelligent with real types here
    if not isinstance(ztype, (_Zarent, type)):
        raise TypeError("{} is not a type or valid ztransformer".format(ztype))
    return {'zerial': {
        'ztype': ztype,
    }}


T = TypeVar('T')
R = TypeVar('R', bound=Sequence[T])
D = TypeVar('D', bound=Sequence[T])
I_T = Iterable[T]


class _Zarent(object):
    """Dumb class to determine soley if the classes are one of ours.

    Don't put anything in it please.
    """


@attr.s
class Zequence(_Zarent, Generic[T, R, D]):
    item_type = attr.ib(type=Type[T])
    reztructure_factory = attr.ib(type=Callable[[I_T], R], default=list)
    deztructure_factory = attr.ib(type=Callable[[I_T], D], default=list)
    apparent_type = attr.ib(type=Type[T])

    @apparent_type.default
    def default_apparent_type(self):
        return MutableSequence[self.item_type]
