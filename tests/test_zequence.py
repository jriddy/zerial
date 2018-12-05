import attr
import pytest

from zerial._data import Zequence
from zerial._core import Ztructurer


@pytest.fixture
def ztr():
    return Ztructurer()


def test_destruct_simple_type(ztr):
    zeq = Zequence(int)
    val = [1, 2, 3, 4]
    dez = zeq.destruct(val, ztr)
    assert dez == val


@attr.s
class Counter(object):
    state = attr.ib(type=int)


def test_destruct_recursive_simple(ztr):
    zeq = Zequence(Counter)
    val = [Counter(x) for x in range(3)]
    dez = zeq.destruct(val, ztr)
    assert dez == [{'state': x} for x in range(3)]


def test_restruct_simple_type(ztr):
    zeq = Zequence(str)
    dat = ['abc', 'def', 'ghi']
    obj = zeq.restruct(dat, ztr)
    assert obj == dat


def test_restruct_recursive_simple(ztr):
    zeq = Zequence(Counter)
    data = [{'state': x} for x in range(5)]
    obj = zeq.restruct(data, ztr)
    assert obj == [Counter(x) for x in range(5)]


def test_destruct_nested_zequence(ztr):
    zeq = Zequence(Zequence(int))
    data = ((1, 5, 9), (2,), (), (18, -19))
    assert zeq.destruct(data, ztr) == [list(xs) for xs in data]


def test_restruct_nested_zequence(ztr):
    zeq = Zequence(Zequence(str, tuple), set)
    data = [["a"], ["b", "c"], [], ["c", "b"]]
    assert zeq.restruct(data, ztr) == {("a",), ("b", "c"), (), ("c", "b")}
