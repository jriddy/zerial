import attr
import pytest

from zerial._data import Zequence
from zerial._core import Ztructurer


@pytest.fixture
def ztr():
    return Ztructurer()


def test_deztruct_simple_type(ztr):
    zeq = Zequence(int)
    val = [1, 2, 3, 4]
    dez = zeq.deztruct(val, ztr)
    assert dez == val


@attr.s
class Counter(object):
    state = attr.ib(type=int)


def test_deztruct_recursive_simple(ztr):
    zeq = Zequence(Counter)
    val = [Counter(x) for x in range(3)]
    dez = zeq.deztruct(val, ztr)
    assert dez == [{'state': x} for x in range(3)]

def test_reztruct_simple_type(ztr):
    zeq = Zequence(str)
    dat = ['abc', 'def', 'ghi']
    obj = zeq.reztruct(dat, ztr)
    assert obj == dat


def test_reztruct_recursive_simple(ztr):
    zeq = Zequence(Counter)
    data = [{'state': x} for x in range(5)]
    obj = zeq.reztruct(data, ztr)
    assert obj == [Counter(x) for x in range(5)]
