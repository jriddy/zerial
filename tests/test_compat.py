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
    type,
    type('RandomClass', (object,), {}),
    ConcreteABC,
])
def test_isconcretetype_positive(t):
    assert isconcretetype(t)


@pytest.mark.parametrize('t', [
    AbstractABC,
    abc.Sequence,
    typing.Sequence,
    # TODO: figure out how to make this test case work
    # typing.Generic,
    # typing.TypeVar,
    # typing.List,
])
def test_isconcretetype_negative(t):
    assert not isconcretetype(t)
