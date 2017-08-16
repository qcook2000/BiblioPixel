import gitty, sys
from . import aliases, importer
from . types.defaults import FIELD_TYPES
from .. animation import runner
from .. import data_maker
from .. layout.geometry import gen_matrix
from .. layout.multimap import MultiMapBuilder
from .. util import files
import copy
from .. import log
import traceback

RESERVED_PROPERTIES = 'name', 'data'


def _make_object(*args, field_types=FIELD_TYPES, **kwds):
    return importer.make_object(*args, field_types=field_types, **kwds)


def _make_layout(layout, driver=None, drivers=None, maker=None):
    if driver is None and drivers is None:
        raise ValueError('Projects has no driver or drivers section')

    coord_map = layout.pop('coordMap', None)

    if drivers is None:
        drivers = [_make_object(**driver)]
    else:
        build = MultiMapBuilder()

        def make_driver(width, height, matrix=None, **kwds):
            build.addRow(gen_matrix(width, height, **(matrix or {})))
            return _make_object(width=width, height=height, **kwds)

        if driver:
            # driver is a default for each driver.
            drivers = [dict(driver, **d) for d in drivers]

        drivers = [make_driver(**d) for d in drivers]
        coord_map = coord_map or build.map
        coord_map = None

    maker = data_maker.Maker(**(maker or {}))
    return _make_object(drivers, coordMap=coord_map, maker=maker, **layout)


def make_animation(layout, animation, run=None):
    reserved = {p: animation.pop(p, None) for p in RESERVED_PROPERTIES}
    animation = _make_object(layout, **animation)

    # Add the reserved properties back in.
    for k, v in reserved.items():
        (v is not None) and setattr(animation, k, v)

    animation.set_runner(runner.Runner(**(run or {})))
    return animation


def _make_project(path=None, animation=None, run=None, **kwds):
    gitty.sys_path.extend(path)
    layout = _make_layout(**kwds)

    return make_animation(layout, animation or {}, run or {})


def project_to_animation(desc, default):
    project = aliases.resolve(default or {}, desc)
    return _make_project(**project)
