from typing import Any

import attr
import pytest

from zerial._data import Zapping


def test_destruct_simple_dict(ztr):
    zap = Zapping(str, str)
    dct = {1: 'a', 2: 'b', 3: 'c'}
    dez = zap.destruct(dct, ztr)
    assert dez == {str(k): v for k, v in dct.items()}


@attr.s
class Counter(object):
    state = attr.ib(type=int)


def test_destruct_zapping_recursive_simple(ztr):
    zap = Zapping(str, Counter)
    val = {k: Counter(ord(k)) for k in 'ABC'}
    dez = zap.destruct(val, ztr)
    assert dez == {
        'A': {'state': 65},
        'B': {'state': 66},
        'C': {'state': 67},
    }


def test_restruct_zapping_int_key(ztr):
    zap = Zapping(int, Counter)
    data = {n: {'state': n} for n in range(1, 25, 5)}
    obj = zap.restruct(data, ztr)
    assert obj == {k: Counter(v['state']) for k, v in data.items()}


def test_restruct_simple_type(ztr):
    zap = Zapping(int, str)
    data = {1: 'a', 2: 'b', 3: 'c'}
    obj = zap.restruct(data, ztr)
    assert obj == data
