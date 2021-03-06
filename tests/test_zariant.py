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


def test_zariant_accepts_arbitrary_named_types(ztr):
    int1, int2 = (type('int', (int,), {}) for _ in range(2))
    # both are named "int"
    zar = Zariant([
        ('int', int1),
        ('integer', int2),
    ])
    assert zar.destruct(int1(2), ztr) == {'%type': 'int', '%value': 2}
    assert zar.destruct(int2(5), ztr) == {'%type': 'integer', '%value': 5}


def test_zariant_restruct_from_dict_definition(ztr):
    zar = Zariant({'ZZ': str, 'NN': int, 'GPN': GenericPersonalName})
    datas = [
        {'%type': 'ZZ', '%value': 'sts'},
        {'%type': 'NN', '%value': 3},
        {'%type': 'GPN', 'name': 'Joe'},
    ]
    assert [zar.restruct(data, ztr) for data in datas] == [
        'sts',
        3,
        GenericPersonalName('Joe'),
    ]


def test_zariant_name_collision_errors(ztr):
    with pytest.raises(TypeError):
        Zariant([('str', type('str', (str,), {})), str])


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


def test_default_type_zariant_simple_type(ztr):
    zar = Zariant([int, str], default=str)
    datas = ['xxx', {'%type': 'int', '%value': 4}]
    assert [zar.restruct(data, ztr) for data in datas] == ['xxx', 4]
