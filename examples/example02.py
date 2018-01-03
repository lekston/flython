#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

from flython import block

from flython.library.planners import WaypointXZ
from flython.library.aerospace.vehicles import Birde

# Set simulation parameters
solver = 'RK45'
t_end = 20
sample_time = .01

# Flight plan definition
plan = [
    WaypointXZ(0, 0),
]

# Initial conditions
u0 = 20.8
w0 = 0.1
q0 = 0
theta0 = np.deg2rad(1)
x0 = 0
z0 = 0
x = np.array([u0, w0, q0, theta0, x0, z0])

# Block definitions
vehicle = block.Definition(
    library='aerospace.eom.SimplifiedLongitudinalMotion',
    parameters=dict(x=x, vehicle=Birde))

flightplan = block.Definition(
    library='planners.PlannerXZ',
    parameters=dict(plan=plan, sample_time=.1))

prev_dtheta = 0
prev_theta_err = 0


def signal_flow(t, n):

    global prev_dtheta, prev_theta_err

    qv, tv, xv, zv = vehicle.x[2:6]
    xr, zr = flightplan(xv)

    # Theta controller
    tr = np.radians(1. + 0.1 * t)
    if np.rad2deg(tr) > 5:
        tr = np.deg2rad(5)
    elif np.rad2deg(tr) < -20:
        tr = np.deg2rad(-20)

    # Pitch controller
    theta_err = (tr - tv)

    dtheta = (prev_theta_err - theta_err) / .01
    dtheta_lp = 0.995 * prev_dtheta + 0.005 * dtheta
    prev_dtheta = dtheta_lp
    prev_theta_err = theta_err
    qr = 0.1 * theta_err - 0.5 * dtheta_lp

    # Elevator controller
    # mr = mcontroller(t, qr - qv)

    # Field of wind
    # wind_vel = windfield(t, xv)
    wind_vel = (0,0)

    # External inputs for vehicle
    u = [2.5, qr, *wind_vel]

    # Vehicle
    T, X = vehicle(u)

    return ([T, [('t', '<f8')]],
            [X, vehicle.dtype],
            [tr, [('tr', '<f8')]],
            [qr, [('qr', '<f8')]],
            [(xr, zr), flightplan.dtype])


if __name__ == '__main__':

    import flython
    import matplotlib.pyplot as plt

    # Run simulation
    simdata = flython.load(__file__).run()

    # Render text using TeX interpreter
    # plt.rc('text', usetex=True)

    # Plot data
    f = plt.figure()

    # plt.plot(simdata['t'], np.sqrt(u**2 + w**2), marker='o')
    plt.plot(simdata['x'], -simdata['z'], marker='o',
             label='Position of a vehicle in vehicle-carried frame')
    plt.plot(simdata['xr'], -simdata['zr'],
             label='Reference trajectory')
    plt.xlabel('x coordinate')
    plt.ylabel('z coordinate')
    plt.grid()
    f.axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
                     ncol=3, fancybox=True, shadow=True)

    f = plt.figure()
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

    f = plt.figure()
    plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
    plt.plot(simdata['t'], np.rad2deg(simdata['theta']),
             label=r"$\Theta(t)$")
    plt.step(simdata['t'], np.rad2deg(simdata['tr']), label=r"$\theta_r(t)$")
    plt.xlabel('t')
    plt.ylabel(r'$\alpha(t), \Theta(t)$')
    f.axes[0].legend()
    plt.grid()

    f = plt.figure()
    plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
    plt.plot(simdata['t'], np.rad2deg(simdata['q']),
             label=r"$q(t)$")
    plt.step(simdata['t'], np.rad2deg(simdata['qr']), label=r"$q_r(t)$")
    plt.xlabel('t')
    plt.ylabel(r'$\alpha(t), q(t)$')
    f.axes[0].legend()
    plt.grid()
    plt.show()
