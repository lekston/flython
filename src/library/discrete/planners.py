import numpy as np

from collections import namedtuple

import library.discrete

WaypointXZ = namedtuple('Waypoint', ['x', 'z'])
WaypointXY = namedtuple('Waypoint', ['x', 'y'])
WaypointXYZ = namedtuple('Waypoint', ['x', 'y', 'z'])


class Constant(library.discrete.Static):

    dtype = [('r', '<f8')]
    _parameters = ['setpoint', 'sample_time']
    _default = dict(sample_time=-1)

    def __init__(self, **parameters):

        def g(x, u):
            return self.setpoint

        super().__init__(g=g, **parameters)


class FlightplanXZ(library.discrete.Static):

    dtype = [('xr', '<f8'), ('zr', '<f8')]
    _parameters = ['plan', 'sample_time']
    _default = dict(sample_time=-1)

    def __init__(self, **parameters):

        def g(x, u):

            # u contains x_vehicle
            return np.array([u, np.interp(u, self.xinterp, self.zinterp)])

        super().__init__(g=g, **parameters)

        self.xinterp = np.array([waypoint.x for waypoint in self.plan])
        self.zinterp = np.array([waypoint.z for waypoint in self.plan])
