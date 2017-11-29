#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

import simulation.api as sim

from continuous import Motor
from models import SimpleMotor

from discrete import P, Planner

# Set simulation parameters
sim.parameters.solver = 'RK45'
sim.parameters.t_end = 10
sim.parameters.step_size = 0.5

# Define fmodel
motor = Motor(SimpleMotor, np.array([0, 0]))
planner = Planner(np.array([1]))
controller = P(np.array([2.]))


def fmodel(t):

    phi = motor.y
    x = motor.x
    ref = planner(t, x)
    err = ref - phi
    u = controller(t, err)
    tm, xm = motor(t, u)

    # Tutaj zwrócić dane do logownia
    return tm, xm

# Run simulation
simdata = sim.run(fmodel)

# Plot data
plt.figure()
plt.plot(simdata['t'], simdata['phi'])
plt.step(simdata['t'], simdata['u'])
plt.show()
