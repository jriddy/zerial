from ._data import zdata, Zequence
from ._core import Ztructurer

__author__ = 'Josh Reed'
__email__ = 'jriddy@gmail.com'
__version__ = '0.0.5'


_the_ztructurer = Ztructurer()
deztructure = _the_ztructurer.deztructure
reztructure = _the_ztructurer.reztructure


__all__ = [
    'deztructure',
    'reztructure',
    'zdata',
    'Zequence',
]
