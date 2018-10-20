import attr
import pytest

from zerial import deztructure, reztructure, zdata, Zequence

@attr.s
class Point3D(object):
    x = attr.ib(type=float)
    y = attr.ib(type=float)
    z = attr.ib(type=float)


p3d_obj = Point3D(0., 1., 2.)
p3d_dct = {'x': 0., 'y': 1., 'z': 2.}

@attr.s
class LineSegment3D(object):
    p1 = attr.ib(type=Point3D)
    p2 = attr.ib(type=Point3D)


lineseg_obj = LineSegment3D(
    Point3D(0., 1., 2.),
    Point3D(1., 2., 0.),
)
lineseg_dct = {
    'p1': {'x': 0., 'y': 1., 'z': 2.},
    'p2': {'x': 1., 'y': 2., 'z': 0.},
}


@attr.s
class NamedPlot(object):
    name = attr.ib(type=str)
    points = attr.ib(
        type=list,
        metadata=zdata(type=Zequence(Point3D)),
    )


@pytest.mark.parametrize('typ,obj,dct', [
    (Point3D, p3d_obj, p3d_dct),
    (LineSegment3D, lineseg_obj, lineseg_dct),
])
def test_symmetrical_stucturing(typ, obj, dct):
    assert deztructure(obj) == dct
    assert reztructure(typ, dct) == obj
