from ._data import zdata, Sequence, Mapping, Variant, Serializer
from ._core import Ztructurer

__author__ = 'Josh Reed'
__email__ = 'jriddy@gmail.com'
__version__ = '0.2.1'


_the_ztructurer = Ztructurer()
destructure = _the_ztructurer.destructure
restructure = _the_ztructurer.restructure
record = _the_ztructurer.record


# TODO: remove aliass in future
Zequence = Sequence
Zapping = Mapping
Zerializer = Serializer
Zariant = Variant


__all__ = [
    'destructure',
    'restructure',
    'record',
    'Sequence',
    'Mapping',
    'Variant',
    'Serializer',
    # TODO: remove difficult aliases in future
    'Ztructurer',
    'zdata',
    'Zapping',
    'Zariant',
    'Zequence',
    'Zerializer',
]
