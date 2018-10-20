import attr
import pytest

from zerial import deztructure, reztructure


@attr.s
class Point3D(object):
    x = attr.ib(type=float)
    y = attr.ib(type=float)
    z = attr.ib(type=float)


p3d_obj = Point3D(0., 1., 2.)
p3d_dct = {'x': 0., 'y': 1., 'z': 2.}


def test_deztructure_basic():
    assert deztructure(p3d_obj) == p3d_dct


def test_reztrucutre_basic():
    assert reztructure(Point3D, p3d_dct) == p3d_obj


@attr.s
class LineSegment3D(object):
    p1 = attr.ib(type=Point3D)
    p2 = attr.ib(type=Point3D)


linseg_obj = LineSegment3D(
    Point3D(0., 1., 2.),
    Point3D(1., 2., 0.),
)
lineseg_dct = {
    'p1': {'x': 0., 'y': 1., 'z': 2.},
    'p2': {'x': 1., 'y': 2., 'z': 0.},
}


def test_deztructure_recursive():
    assert deztructure(linseg_obj) == lineseg_dct


@pytest.mark.skip
def test_rezstructure_recursive():
    assert reztructure(LineSegment3D, lineseg_dct) == linseg_obj
