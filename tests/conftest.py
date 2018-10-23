import pytest

from zerial._core import Ztructurer


@pytest.fixture
def ztr():
    """Unique Ztructurer for tests that need it."""
    return Ztructurer()
