from typing import Union

import attr
import pytest

from zerial._data import Zariant
from zerial._core import Ztructurer


@pytest.fixture
def ztr():
    return Ztructurer(metachar='%')


def test_zariant_has_types():
    zar = Zariant([int, float])
    assert zar.types == (int, float)


def test_zariant_rejects_non_types():
    with pytest.raises(TypeError):
        Zariant([1, 2])


def test_zariant_requires_concrete_types():
    with pytest.raises(TypeError):
        Zariant([int, type])


@pytest.mark.parametrize('types', [
    [],
    [int],
])
def test_zariant_requires_multiple_types(types):
    with pytest.raises(ValueError):
        Zariant(types)


def test_zariant_requires_unique_types():
    with pytest.raises(TypeError):
        Zariant([int, int])


def test_zariant_requires_unique_names():
    with pytest.raises(TypeError):
        Zariant([int, type('int', (object,), {})])


def test_zariant_of_simple_types(ztr):
    zar = Zariant([int, float])
    assert zar.destruct(3, ztr) == {'%type': 'int', '%value': 3}
    assert zar.destruct(1., ztr) == {'%type': 'float', '%value': 1.}


@attr.s
class ClassicPersonalName(object):
    first_name = attr.ib(type=str)
    last_name = attr.ib(type=str)


@attr.s
class GenericPersonalName(object):
    name = attr.ib(type=str)


def test_zariant_of_complex_types(ztr):
    zar = Zariant([ClassicPersonalName, GenericPersonalName])
    cpn = ClassicPersonalName('Random', 'Person')
    gpn = GenericPersonalName('GeneralCoolFactor')
    assert zar.destruct(cpn, ztr) == {
        '%type': 'ClassicPersonalName',
        'first_name': 'Random',
        'last_name': 'Person',
    }
    assert zar.destruct(gpn, ztr) == {
        '%type': 'GenericPersonalName',
        'name': 'GeneralCoolFactor',
    }


def test_zariant_restrucutres_simple_types(ztr):
    zar = Zariant([int, str])
    assert zar.restruct({'%type': 'int', '%value': 3}, ztr) == 3
    assert zar.restruct({'%type': 'str', '%value': '3'}, ztr) == '3'


def test_zariant_restructures_complex_types(ztr):
    zar = Zariant([ClassicPersonalName, GenericPersonalName])
    cpn_dct = {
        '%type': 'ClassicPersonalName',
        'first_name': 'Random',
        'last_name': 'Person',
    }
    gpn_dct = {
        '%type': 'GenericPersonalName',
        'name': 'GeneralCoolFactor',
    }
    cpn_obj = ClassicPersonalName('Random', 'Person')
    gpn_obj = GenericPersonalName('GeneralCoolFactor')
    assert zar.restruct(cpn_dct, ztr) == cpn_obj
    assert zar.restruct(gpn_dct, ztr) == gpn_obj


def test_zariant_gives_union_as_apparent_type():
    zar = Zariant([int, ClassicPersonalName, str])
    assert zar.apparent_type == Union[int, ClassicPersonalName, str]
