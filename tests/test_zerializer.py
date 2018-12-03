import pytest

from zerial._core import Ztructurer
from zerial._data import Zerializer


@pytest.fixture
def m_ztructurer(mocker):
    return mocker.Mock(Ztructurer)


def test_zerializer_can_do_dumb_stuff(m_ztructurer):
    zer = Zerializer(lambda x: x + 1, lambda x: x * 2)
    outer = zer.destruct(4, m_ztructurer)
    inner = zer.restruct(outer, m_ztructurer)
    assert (outer, inner) == (5, 10)
    assert not m_ztructurer.mock_calls


def test_zerializer_handles_things_like_tuples(m_ztructurer):
    zer = Zerializer(list, tuple)
    val = (1, 2, 3)
    outer = zer.destruct(val, m_ztructurer)
    assert outer == [1, 2, 3]
    assert zer.restruct(outer, m_ztructurer) == val
