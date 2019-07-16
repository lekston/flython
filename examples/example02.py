#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

from flython import block

from flython.library.planners import WaypointXZ
from flython.library.aerospace.vehicles import Birdie

# Set simulation parameters
solver = 'RK45'
t_end = 20
sample_time = .1

# Flight plan definition
plan = [
    WaypointXZ(0, 0),
]

# Initial conditions
u0 = 20.89
w0 = 0.085
q0 = 0
theta0 = np.deg2rad(1)
x0 = 0
z0 = 0
x = np.array([u0, w0, q0, theta0, x0, z0])

# Block definitions
vehicle = block.Definition(
    library='aerospace.eom.SimplifiedLongitudinalMotion',
    parameters=dict(x=x, vehicle=Birdie))

flightplan = block.Definition(
    library='planners.PlannerXZ',
    parameters=dict(plan=plan, sample_time=.1))

controller = block.Definition(
    library='controllers.PIDRealEuler',
    parameters=dict(Kp=.1, Ki=0, Kd=.5, alpha=.005, sample_time=.1))


def signal_flow(t, n):

    qv, tv, xv, zv = vehicle.x[2:6]
    xr, zr = flightplan(xv)

    # Theta controller
    tr = np.radians(1.2)

    if np.rad2deg(tr) > 5:
        tr = np.deg2rad(5)
    elif np.rad2deg(tr) < -20:
        tr = np.deg2rad(-20)

    # Pitch rate controller
    u = tr - tv
    qr = controller(u)

    # Wind velocity
    wind_vel = (0, 0)

    # External inputs for vehicle
    u = [2.2, qr, *wind_vel]

    # Vehicle
    T, X = vehicle(u)

    return ([T, [('t', '<f8')]],
            [X, vehicle.dtype],
            [tr, [('tr', '<f8')]],
            [qr, [('qr', '<f8')]],
            [(xr, zr), flightplan.dtype])


def run_n_plot():

    import flython
    import matplotlib.pyplot as plt

    # Run simulation
    simdata = flython.load(__file__).run()

    # Plot data
    f = plt.figure(1)
    f.clear()

    # plt.plot(simdata['t'], np.sqrt(u**2 + w**2), marker='o')
    plt.plot(simdata['x'], -simdata['z'], marker='o',
             label='Position of a vehicle in earth-fixed frame')
    plt.plot(simdata['xr'], -simdata['zr'],
             label='Reference trajectory')
    plt.xlabel('x coordinate')
    plt.ylabel('z coordinate')
    plt.grid()
    f.axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
                     ncol=3, fancybox=True, shadow=True)

    f = plt.figure(2)
    f.clear()
    # plt.plot(simdata['t'], simdata['z'], marker='o')
    u = simdata['u']
    w = simdata['w']
    plt.plot(simdata['t'], simdata['u'], label='$u(t)$')
    plt.plot(simdata['t'], simdata['w'], label='$w(t)$')
    plt.plot(simdata['t'], np.sqrt(u**2 + w**2), label=r'$\mathrm{TAS}(t)$')
    plt.xlabel('t')
    plt.ylabel(r'$u(t), w(t), \mathrm{TAS}(t)$')
    f.axes[0].legend()
    plt.grid()

    f = plt.figure(3)
    f.clear()
    plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
    plt.plot(simdata['t'], np.rad2deg(simdata['theta']),
             label=r"$\Theta(t)$")
    plt.step(simdata['t'], np.rad2deg(simdata['tr']), label=r"$\theta_r(t)$")
    plt.xlabel('t')
    plt.ylabel(r'$\alpha(t), \Theta(t)$')
    f.axes[0].legend()
    plt.grid()

    f = plt.figure(4)
    f.clear()
    plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
    plt.plot(simdata['t'], np.rad2deg(simdata['q']),
             label=r"$q(t)$")
    plt.step(simdata['t'], np.rad2deg(simdata['qr']), label=r"$q_r(t)$")
    plt.xlabel('t')
    plt.ylabel(r'$\alpha(t), q(t)$')
    f.axes[0].legend()
    plt.grid()
    plt.show(block=False)

if __name__ == '__main__':
    run_n_plot()
