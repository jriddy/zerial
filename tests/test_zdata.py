import pytest

from zerial import zdata


def test_zdata_takes_types():
    zd = zdata(ztype=int)
    assert zd == {'zerial': {'ztype': int}}


@pytest.mark.parametrize('obj', [
    1, 1., '', (), [], {}, lambda: None, object()
])
def test_zdata_rejects_non_types(obj):
    with pytest.raises(TypeError):
        zdata(ztype=obj)
