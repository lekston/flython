#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

from flython.core import block

# Set simulation parameters
solver = 'RK45'
t_end = 20
sample_time = .5

# Block definitions
# Example 1: block definition using arguments
motor = block.Definition(
    library='examples.Motor',
    parameters=dict(x=np.zeros(2), friction=1)
)

# Example 2: block definition using attributes
planner = block.Definition()
planner.library = 'planners.Constant'
planner.parameters = dict(setpoint=1.0)

controller = block.Definition()
controller.library = 'controllers.PIrD'
controller.parameters = dict(Kp=1, Ki=0, Kd=.2)


def signal_flow(t, n):

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

    import flython
    import matplotlib.pyplot as plt

    # Run simulation
    simdata = flython.load(__file__).run()

    # Plot data
    plt.figure()
    plt.plot(simdata['t'], simdata['phi'], marker='o')
    plt.step(simdata['t'], simdata['u'])
    plt.step(simdata['t'], simdata['r'])
    plt.grid()
    plt.show()
