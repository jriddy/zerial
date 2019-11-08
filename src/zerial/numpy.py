from __future__ import absolute_import

from operator import attrgetter, methodcaller
import sys

import attr
import numpy as np  # fail early if not installed

from ._core import DEFAULT_PASSTHRUS, Ztructurer


# Shamelessly stolen from https://github.com/lebedov/msgpack-numpy

if sys.version_info >= (3, 0):
    # Your serialization layer is going to have to support binary data
    numpy_required_passthrus = DEFAULT_PASSTHRUS + (bytes,)

    if sys.platform == 'darwin':
        # TODO: Can we really not rely on the data on darwin?
        ndarray_to_bytes = methodcaller('tobytes')
    else:
        # TODO: we can probably get away with saving f_contiguous
        # if we reconstruct correctly on the other side
        ndarray_to_bytes = lambda x: (
            x.data if x.flags.c_contiguous else x.tobytes()
        )

    num_to_bytes = attrgetter('data')

    # TODO: do we need this
    def tostr(x):
        if isinstance(x, bytes):
            return x.decode()
        else:
            return str(x)
else:
    numpy_required_passthrus = DEFAULT_PASSTHRUS

    if sys.platform == 'darwin':
        ndarray_to_bytes = methodcaller('tobytes')
    else:
        ndarray_to_bytes = lambda x: (
            memoryview(x.data) if x.flags.c_contiguous else x.tobytes()
        )

    num_to_bytes = lambda obj: memoryview(obj.data)

    tostr = lambda x: x


def buffer_to_ndarray(v, *xs, **kw):
    v = v.tobytes() if isinstance(v, memoryview) else v
    # We have to copy to get an "owned", writable array
    # TODO: find a better way around this that isn't as expensive
    return np.frombuffer(v, *xs, **kw).copy()


@attr.s
class NdarrayEncoder(object):
    def encode(self, inst, ztr):
        if inst.dtype.hasobject:
            raise TypeError(
                "cowardly refusing to destructure ndarry containing "
                "Python objects"
            )
        if inst.dtype.kind == 'V':
            descr = inst.dtype.descr
        else:
            descr = inst.dtype.str
        gm = ztr.get_metakey
        return ztr.dict_factory([
            (gm('dtype'), descr),
            (gm('shape'), inst.shape),
            (gm('data'), ndarray_to_bytes(inst)),
        ])

    def decode(self, data, ztr):
        gm = ztr.get_metakey
        raw_dtype = data[gm('dtype')]
        if isinstance(raw_dtype, list):
            descr = [tuple(map(tostr, dt)) for dt in raw_dtype]
        else:
            descr = raw_dtype
        return buffer_to_ndarray(
            data[gm('data')],
            dtype=np.dtype(descr),
        ).reshape(data[gm('shape')])

    def tobytes(self, data, descr, shape):
        # Experimental method
        return b'\n'.join([
            b"ndarray",
            str(descr).encode(),
            str(shape).encode(),
            b'',
            data,
        ])


the_numpy_structurer = Ztructurer(
    permitted_passthrus=numpy_required_passthrus,
    encoders={np.ndarray: NdarrayEncoder()}
)
