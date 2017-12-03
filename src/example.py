#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation.api as sim

from library.continuous.models import SimpleMotor
from library.discrete.planners import Constant
from library.discrete.controllers import P

# Set simulation parameters
sim.parameters.solver = 'RK45'
sim.parameters.t_end = 10
sim.parameters.sample_time = 1

# Define fmodel
motor = SimpleMotor(x=np.zeros(2), friction=1)
controller = P(gain=1.0, sample_time=1)
planner = Constant(setpoint=1.0, sample_time=2)


def fmodel(t):

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


# Run simulation
simdata = sim.run(fmodel)

# Plot data
plt.figure()
plt.plot(simdata[0]['t'], simdata[0]['phi'], marker='o')
plt.step(simdata[0]['t'], simdata[0]['u'])
plt.step(simdata[0]['t'], simdata[0]['r'])
plt.grid()
plt.show()
