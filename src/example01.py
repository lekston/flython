#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

import simulation

from library.blocks import BlockDef

# Set simulation parameters
simulation.parameters.solver = 'RK45'
simulation.parameters.t_end = 10
simulation.parameters.sample_time = 1

# Block definitions
# Example 1: block definition using arguments
motor = BlockDef(
    library='library.examples.Motor',
    parameters=dict(x=np.zeros(2), friction=1)
)

# Example 2: block definition using attributes
planner = BlockDef()
planner.library = 'library.planners.Constant'
planner.parameters = dict(setpoint=1.0)

controller = BlockDef()
controller.library = 'library.controllers.P'
controller.parameters = dict(Kp=1.0)


def signal_flow():

    phi = motor.y
    x = motor.x
    ref = planner(x)
    err = ref - phi
    u = controller(err)
    T, X = motor(u)

    return ([T, [('t', '<f8')]],
            [X, motor.dtype],
            [u, controller.dtype],
            [ref, planner.dtype])


if __name__ == '__main__':

    import sys
    import matplotlib.pyplot as plt

    # Run simulation
    simdata = simulation.Simulation(sys.modules[__name__]).run()

    # Plot data
    plt.figure()
    plt.plot(simdata['t'], simdata['phi'], marker='o')
    plt.step(simdata['t'], simdata['u'])
    plt.step(simdata['t'], simdata['r'])
    plt.grid()
    plt.show()
