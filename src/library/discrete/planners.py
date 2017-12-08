import numpy as np

from collections import namedtuple

import library.discrete

from core import pslots

WaypointXZ = namedtuple('Waypoint', ['x', 'z'])
WaypointXY = namedtuple('Waypoint', ['x', 'y'])
WaypointXYZ = namedtuple('Waypoint', ['x', 'y', 'z'])


class Constant(library.discrete.Static):

    dtype = [('r', '<f8')]

    def __init__(self, setpoint, sample_time=-1):

        self.parameters = pslots(
            setpoint=setpoint, sample_time=sample_time)

        def g(x, u):
            return self.parameters.setpoint

        super().__init__(g=g)


class FlightplanXZ(library.discrete.Static):

    dtype = [('xr', '<f8'), ('zr', '<f8')]

    def __init__(self, plan, sample_time=-1):

        self.parameters = pslots(
            plan=plan, sample_time=sample_time)

        self.xinterp = np.array([waypoint.x for waypoint in plan])
        self.zinterp = np.array([waypoint.z for waypoint in plan])

        def g(x, u):

            # u contains x_vehicle
            return np.array([u, np.interp(u, self.xinterp, self.zinterp)])

        super().__init__(g=g)
