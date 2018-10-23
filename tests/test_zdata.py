import pytest

from zerial._data import zdata, Zendthru, Zariant


def test_zdata_takes_regular_types_as_zendthrus():
    zd = zdata(ztype=int)
    assert zd == {'zerial.ztype': Zendthru(int)}


def test_zdata_leaves_ztypes_just_there():
    Zif = Zariant([int, float])
    zd = zdata(ztype=Zif)
    assert zd == {'zerial.ztype': Zif}


@pytest.mark.parametrize('obj', [
    1, 1., '', (), [], {}, lambda: None, object()
])
def test_zdata_rejects_non_types(obj):
    with pytest.raises(TypeError):
        zdata(ztype=obj)
