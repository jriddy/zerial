import datetime

import pytest

from zerial._data import Zendthru


@pytest.mark.parametrize('method', ['destruct', 'restruct'])
def test_zendthru_passes_thru(ztr, method):
    thru = Zendthru(datetime.datetime)
    dt = datetime.datetime(2004, 5, 12, 18, 30, 5)
    assert getattr(thru, method)(dt, ztr) == dt


@pytest.mark.parametrize('method', ['destruct', 'restruct'])
def test_zendthru_rejects_not_passing_type(ztr, method):
    thru = Zendthru(datetime.date)
    delta = datetime.timedelta(1)
    with pytest.raises(TypeError):
        getattr(thru, method)(delta, ztr)
