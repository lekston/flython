#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np
import matplotlib.pyplot as plt

import simulation.api as sim

from continuous import Motor
from models import SimpleMotor

from discrete import P, Planner

# Set simulation parameters
sim.parameters.solver = 'RK45'
sim.parameters.t_end = 10
sim.parameters.step_size = 1

# Define fmodel
motor = Motor(SimpleMotor, np.array([0, 0]))
planner = Planner(np.array([1]))
controller = P(np.array([1.]))


def fmodel(t):

    phi = motor.y
    x = motor.x
    ref = planner(t, x)
    err = ref - phi
    u = controller(t, err)
    T, X = motor(t, u)

    return (T,
            [X, motor.dtype],
            [u, controller.dtype],
            [ref, planner.dtype])


# Run simulation
simdata = sim.run(fmodel)

# Plot data
plt.figure()
plt.plot(simdata[0]['t'], simdata[0]['phi'], marker='o')
plt.step(simdata[0]['t'], simdata[0]['u1'])
plt.step(simdata[0]['t'], simdata[0]['r'])
plt.grid()
plt.show()
