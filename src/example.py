#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation

from library.continuous.models import SimpleMotor
from library.discrete.planners import Constant
from library.discrete.controllers import P

# Set simulation parameters
simulation.parameters.solver = 'RK45'
simulation.parameters.t_end = 10
simulation.parameters.sample_time = 1

# Define fmodel
motor = SimpleMotor(x=np.zeros(2), friction=1)
controller = P(gain=1.0)
planner = Constant(setpoint=1.0)


class Model:

    contains = [motor, controller, planner]

    @staticmethod
    def signal_flow(t):

        phi = motor.y
        x = motor.x
        ref = planner(t, x)
        err = ref - phi
        u = controller(t, err)
        T, X = motor(t, u)

        return ([T, [('t', '<f8')]],
                [X, motor.dtype],
                [u, controller.dtype],
                [ref, planner.dtype])


sim = simulation.Manager(Model)
simdata = sim.run()

# Plot data
plt.figure()
plt.plot(simdata[0]['t'], simdata[0]['phi'], marker='o')
plt.step(simdata[0]['t'], simdata[0]['u'])
plt.step(simdata[0]['t'], simdata[0]['r'])
plt.grid()
plt.show()
