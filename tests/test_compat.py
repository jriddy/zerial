from abc import ABCMeta, abstractmethod
try:
    from collections import abc
except ImportError:
    import collections as abc
import typing

import pytest

from zerial._compat import isconcretetype, with_metaclass


ABC = with_metaclass(ABCMeta)


class ConcreteABC(ABC):
    """Yes this is possible! Thanks python!"""


class AbstractABC(ABC):
    @abstractmethod
    def method(self):
        pass


@pytest.mark.parametrize('t', [
    object,
    int,
    str,
    tuple,
    list,
    dict,
    type(None),
    type('RandomClass', (object,), {}),
    ConcreteABC,
])
def test_isconcretetype_positive(t):
    assert isconcretetype(t)


@pytest.mark.parametrize('t', [
    type,
    type('my_metaclass', (type,), {}),
    lambda: None,
    ABCMeta,
    AbstractABC,
    abc.Sequence,
    typing.Sequence,
    typing.Union,
    typing.Generic,
    typing.List,
    typing.TypeVar,
    typing.TypeVar('T'),
    typing.NewType('Int', int),
])
def test_isconcretetype_negative(t):
    assert not isconcretetype(t)
