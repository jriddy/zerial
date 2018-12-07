import attr
import pytest

from zerial import (
    destructure, restructure, zdata, Zequence, Zariant, Zapping, Zerializer,
)


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
    ignored_field = attr.ib(init=False, cmp=False, repr=False)


namedplot_obj = NamedPlot(
    name='Bobo',
    points=[
        Point3D(0., 0., 0.),
        Point3D(0., 1., 0.),
        Point3D(0., 1., 1.),
        Point3D(0., 0., 1.),
    ],
)
namedplot_obj.ignored_field = 'asfdklj'
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
    _lang = attr.ib(type=str, default='en')


@attr.s
class MeasurementsSize(object):
    waist = attr.ib(type=int)
    inseam = attr.ib(type=int)


SizeVariant = Zariant([LetterSize, MeasurementsSize])


@attr.s
class ColoredPants(object):
    color = attr.ib(type=str)
    size = attr.ib(
        type=SizeVariant.apparent_type,
        metadata=zdata(ztype=SizeVariant),
    )


bluepants_obj = ColoredPants(
    color='blue',
    size=LetterSize('L'),
)
bluepants_dct = {
    'color': 'blue',
    'size': {
        '%type': 'LetterSize',
        'size': 'L',
        'lang': 'en',
    },
}

redpants_obj = ColoredPants(
    color='red',
    size=MeasurementsSize(waist=34, inseam=32),
)
redpants_dct = {
    'color': 'red',
    'size': {
        '%type': 'MeasurementsSize',
        'waist': 34,
        'inseam': 32,
    },
}


@attr.s
class CaptureTable(object):
    name = attr.ib(type=str)
    captures = attr.ib(metadata=zdata(Zequence(Zapping(int, str))))


capture_table_obj = CaptureTable(
    name='caps-01',
    captures=[
        {
            1: 'one;A',
            5: 'five;E',
            12: 'twelve;L',
        },
        {
            18: 'eighteen;S',
        },
    ],
)
capture_table_dct = {
    'name': 'caps-01',
    'captures': [
        {
            '1': 'one;A',
            '5': 'five;E',
            '12': 'twelve;L',
        },
        {
            '18': 'eighteen;S',
        },
    ],
}


if isinstance(range(1), list):
    # Python 2 ``xrange`` does not implement ``__eq__`` itself
    # We don't a fully featured range object, just one that serializes
    @attr.s
    class Range(object):
        start = attr.ib()
        stop = attr.ib()
        step = attr.ib(default=1)

        @stop.default
        def _stop_default(self):
            stop, self.start = self.start, 0
            return stop
else:
    Range = range


range_zerializer = Zerializer(
    lambda rng: [rng.start, rng.stop, rng.step],
    lambda lst: Range(*lst),
)


@attr.s
class RangeContainer(object):
    indices = attr.ib(type=dict, metadata=zdata(Zapping(int, range_zerializer)))
    identifiers = attr.ib(type=dict,
                          metadata=zdata(Zapping(str, Zequence(int))))


range_container_obj = RangeContainer(
    {2: Range(1, 10), 4: Range(28, 21, -1)},
    {'abc': [4, 5, 6, 9]},
)
range_container_dct = {
    'indices': {'2': [1, 10, 1], '4': [28, 21, -1]},
    'identifiers': {'abc': [4, 5, 6, 9]}
}


# What is below is just a way to collect these zstructs and their destructured
# dicts into a flattened list of parameters for the structuring symmetry
# test function.  This lets "parametrize" turn each combo into a test case
example_ztructs = [
    (Point3D, p3d_obj, p3d_dct),
    (LineSegment3D, lineseg_obj, lineseg_dct),
    (NamedPlot, namedplot_obj, namedplot_dct),
    (ColoredPants, bluepants_obj, bluepants_dct),
    (ColoredPants, redpants_obj, redpants_dct),
    (CaptureTable, capture_table_obj, capture_table_dct),
    (RangeContainer, range_container_obj, range_container_dct),
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
