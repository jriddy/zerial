import pytest

import attr
import numpy as np

from zerial.numpy import NdarrayEncoder, the_numpy_structurer


@pytest.fixture
def encoder():
    return NdarrayEncoder()


@pytest.fixture
def npztr():
    return the_numpy_structurer


def test_encoder_barfs_on_refcounted_python_objects_in_array(encoder, npztr):
    arr = np.array([object()])
    with pytest.raises(TypeError) as ce:
        encoder.encode(arr, npztr)
    assert str(ce.value).startswith("cowardly refusing")


@pytest.mark.parametrize('arr', [
    np.array([]),
    np.empty((1024, 256, 16), dtype=np.float64),
    np.random.random((10, 10, 10)),
    np.random.random((5, 15, 2)).T,
    # TODO: add more tests here
])
def test_encode_decode_stability(arr, encoder, npztr):
    encoded = encoder.encode(arr, npztr)
    if isinstance(encoded['%data'], memoryview):
        # force memory read
        encoded['%data'] = encoded['%data'].tobytes()
    decoded = encoder.decode(encoded, npztr)
    assert (arr == decoded).all()


def test_encodes_toplevel_when_given_as_type(npztr, encoder):
    arr = np.array(range(10), dtype=np.int_)
    des = npztr.destructure(arr, np.ndarray)
    enc = encoder.encode(arr, npztr)
    assert des == enc


def test_encodes_toplevel_fails_when_not_given_as_type(npztr, encoder):
    arr = np.linspace(0, 1)
    with pytest.raises(attr.exceptions.NotAnAttrsClassError):
        npztr.destructure(arr)


@attr.s(eq=False)
class Example(object):
    arr = attr.ib(type=np.ndarray)
    other = attr.ib(type=str, default='')

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.other == other.other and
            (self.arr == other.arr).all()
        )


def test_can_encode_structured_ndarray(npztr):
    example = Example(np.array([1, 19, 18]))
    destructed = npztr.destructure(example)
    restructed = npztr.restructure(Example, destructed)
    assert example == restructed


def test_restructured_array_is_writable(npztr):
    arr = np.array([1, 2], dtype=np.int_)
    example = Example(arr)
    destructured = npztr.destructure(example)
    restructured = npztr.restructure(Example, destructured)
    new_arr = restructured.arr
    new_arr += 2
    assert ((arr + 2) == new_arr).all()
