#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation

from library.continuous.models import SimplifiedLongitudinalMotion
from library.discrete.planners import WaypointXZ, FlightplanXZ
from library.discrete.controllers import P
from library.vehicles import Birde

# Set simulation parameters
simulation.parameters.solver = 'RK45'
simulation.parameters.t_end = 10
simulation.parameters.sample_time = 1

# Define flight plan
plan = [
    WaypointXZ(0, 300),
    WaypointXZ(500, 300),
    WaypointXZ(700, 200),
    WaypointXZ(1200, 200)
]
# Initial conditions
x = None

# Define Model
vehicle = SimplifiedLongitudinalMotion(x, system=Birde)
controller = P(gain=1.0)
planner = FlightplanXZ(plan=plan)


class Model:

    contains = [vehicle, controller, planner]

    @staticmethod
    def signal_flow(t):

        x = vehicle.x
        ref = planner(t, x)

        # Dorobić pętlę sterujące
        T, X = vehicle(t, u)

        return ([T, [('t', '<f8')]],
                [X, vehicle.dtype],
                [ref, planner.dtype])


simdata = simulation.Simulation(Model).run()

# Plot data
plt.figure()
plt.plot(simdata[0]['t'], simdata[0]['phi'], marker='o')
plt.step(simdata[0]['t'], simdata[0]['u'])
plt.step(simdata[0]['t'], simdata[0]['r'])
plt.grid()
plt.show()
