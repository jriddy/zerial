import pytest

from zerial import zdata


def test_zdata_takes_types():
    zd = zdata(type=int)
    assert zd == {'zerial': {'type': int}}


@pytest.mark.parametrize('obj', [
    1, 1., '', (), [], {}, lambda: None, object()
])
def test_zdata_rejects_non_types(obj):
    with pytest.raises(TypeError):
        zdata(type=obj)
