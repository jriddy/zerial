import attr
import pytest

from zerial._core import Ztructurer


@pytest.mark.parametrize('val', [
    1, 1., '', True, False,
])
def test_can_pass_thru_positive(ztr, val):
    assert ztr.can_pass_thru(val)


bad_values = [
    None, lambda: None, object(), {}
]


@pytest.mark.parametrize('val', bad_values)
def test_can_pass_thru_negative(ztr, val):
    assert not ztr.can_pass_thru(val)


@attr.s
class Ex1(object):
    x = attr.ib()
    y = attr.ib()


def test_can_destructure_friendly_adhoc_record(ztr):
    ex = Ex1(1, 'x')
    assert ztr.destructure(ex) == {'x': 1, 'y': 'x'}


@pytest.mark.parametrize('val', bad_values)
def test_cannot_destructure_objecty_adhoc_record(ztr, val):
    ex = Ex1(val, 'hmmmm')
    with pytest.raises(TypeError) as einfo:
        ztr.destructure(ex)
    assert str(einfo.value).startswith('cannot destructure')


@attr.s
class Ex2(object):
    public = attr.ib()
    _protected = attr.ib()
    __private = attr.ib()
    __dunder__ = attr.ib()


def test_format_field_name(ztr):
    ex2_obj = Ex2(1, 2, 3, 4)
    ex2_dct = {
        'public': 1,
        'protected': 2,
        'Ex2__private': 3,
        'dunder__': 4,
    }
    assert ztr.destructure(ex2_obj) == ex2_dct
    assert ztr.restructure(Ex2, ex2_dct) == ex2_obj
