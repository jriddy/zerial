import attr
import pytest

from zerial import destructure, restructure, zdata, Zequence, Zariant

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

namedplot_obj = NamedPlot(
    name='Bobo',
    points=[
        Point3D(0., 0., 0.),
        Point3D(0., 1., 0.),
        Point3D(0., 1., 1.),
        Point3D(0., 0., 1.),
    ],
)
namedplot_dct = {
    'name': 'Bobo',
    'points': [
        {'x': 0., 'y': 0., 'z': 0.},
        {'x': 0., 'y': 1., 'z': 0.},
        {'x': 0., 'y': 1., 'z': 1.},
        {'x': 0., 'y': 0., 'z': 1.},
    ],
}


SizeOptions = {'XS', 'S', 'M', 'L', 'XL'}


@attr.s
class LetterSize(object):
    # TODO: define an Enum when we can handle it
    size = attr.ib(type=str, validator=attr.validators.in_(SizeOptions))


@attr.s
class MeasurementsSize(object):
    waist = attr.ib(type=int)
    inseam = attr.ib(type=int)


SizeVariant = Zariant([LetterSize, MeasurementsSize])


# What is below is just a way to collect these zstructs and their destructured
# dicts into a flattened list of parameters for the structuring symmetry
# test function.  This lets "parametrize" turn each combo into a test case
example_ztructs = [
    (Point3D, p3d_obj, p3d_dct),
    (LineSegment3D, lineseg_obj, lineseg_dct),
    (NamedPlot, namedplot_obj, namedplot_dct),
]
example_ztructs_with_directions = [
    [(typ, obj, dct, dir) for dir in ('destructure', 'restructure')]
    for typ, obj, dct in example_ztructs
]
flattened_example_ztructs_with_directions = [
    x for xs in example_ztructs_with_directions for x in xs
]

@pytest.mark.parametrize('typ,obj,dct,dir',
                         flattened_example_ztructs_with_directions)
def test_structuring_symmetry(typ, obj, dct, dir):
    if dir == 'destructure':
        assert destructure(obj) == dct
    elif dir == 'restructure':
        assert restructure(typ, dct) == obj
    else:
        raise ValueError("malformed test: unknown dir: %s" % (dir,))
