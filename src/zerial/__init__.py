from ._data import zdata, Zequence, Zapping, Zariant, Zerializer
from ._core import Ztructurer

__author__ = 'Josh Reed'
__email__ = 'jriddy@gmail.com'
__version__ = '0.1.6'


_the_ztructurer = Ztructurer()
destructure = _the_ztructurer.destructure
restructure = _the_ztructurer.restructure


__all__ = [
    'destructure',
    'restructure',
    'Ztructurer',
    'zdata',
    'Zapping',
    'Zariant',
    'Zequence',
    'Zerializer',
]
