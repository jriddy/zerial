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
        metadata=zdata(ztype=Zequence(Point3D)),
    )


# What is below is just a way to collect these zstructs and their destructured
# dicts into a flattened list of parameters for the structuring symmetry
# test function.  This lets "parametrize" turn each combo into a test case
example_ztructs = [
    (Point3D, p3d_obj, p3d_dct),
    (LineSegment3D, lineseg_obj, lineseg_dct),
]
example_ztructs_with_directions = [
    [(typ, obj, dct, dir) for dir in ('deztructure', 'reztructure')]
    for typ, obj, dct in example_ztructs
]
flattened_example_ztructs_with_directions = [
    x for xs in example_ztructs_with_directions for x in xs
]

@pytest.mark.parametrize('typ,obj,dct,dir',
                         flattened_example_ztructs_with_directions)
def test_structuring_symmetry(typ, obj, dct, dir):
    if dir == 'deztructure':
        assert deztructure(obj) == dct
    elif dir == 'reztructure':
        assert reztructure(typ, dct) == obj
    else:
        raise ValueError("malformed test: unknown dir: %s" % (dir,))
