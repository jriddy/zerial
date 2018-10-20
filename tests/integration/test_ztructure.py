import attr

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
