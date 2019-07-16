#!/opt/local/bin/python
# This is a simple simulation script, tested in Python 3.6.3
import numpy as np

from flython import block

from flython.library.planners import WaypointXZ
from flython.library.aerospace.vehicles import Birdie

# Set simulation parameters
solver = 'RK45'
t_end = 60
sample_time = .01

# Flight plan definition
plan = [
    WaypointXZ(0,     0),
    WaypointXZ(300,  -5),
    WaypointXZ(700,   15),
    WaypointXZ(4000,  10)
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
    parameters=dict(plan=plan, sample_time=.02))

prev_dalt_lp = 0
prev_alt_err = 0

prev_dtheta_lp = 0
prev_theta_err = 0

prev_t = 0
prev_tr = 0
prev_qr = 0

ctrl_t_step = 0.02

def signal_flow(t, n):

    global prev_dalt_lp, prev_alt_err, prev_dtheta_lp, prev_theta_err

    global prev_t, prev_tr, prev_qr

    qv, tv, xv, zv = vehicle.x[2:6]
    xr, zr = flightplan(xv)

    dt = t - prev_t

    if abs(dt - ctrl_t_step) < 0.01*ctrl_t_step:
        prev_t = t

        ### TODO:
        # when doing time stepping from here the flightplan & controllers fall out of sync

        # Altitude controller
        alt_err = - (zr - zv) # change sign due to theta convetion (pos theta yields climb -> i.e. neg. z)
        d_alt = (alt_err - prev_alt_err) / dt
        prev_alt_err = alt_err

        d_alt_lp = 0.98 * prev_dalt_lp + 0.02 * d_alt
        prev_dalt_lp = d_alt_lp
        tr = .01 * alt_err + .05 * d_alt_lp
        prev_tr = tr

        # Pitch controller
        theta_err = (tr - tv)
        dtheta = (theta_err - prev_theta_err) / dt
        prev_theta_err = theta_err

        dtheta_lp = 0.95 * prev_dtheta_lp + 0.05 * dtheta
        prev_dtheta_lp = dtheta_lp
        qr = .1 * theta_err + .5 * dtheta_lp
        prev_qr = qr

    else:
        tr = prev_tr
        qr = prev_qr

    # Saturate q_dem
    if np.rad2deg(qr) > 45:
        qr = np.deg2rad(45)
    elif np.rad2deg(qr) < -45:
        qr = np.deg2rad(-45)

    # Saturate q_dem
    if np.rad2deg(tr) > 20:
        tr = np.deg2rad(20)
    elif np.rad2deg(tr) < -15:
        tr = np.deg2rad(-15)

    # Elevator controller
    # mr = mcontroller(t, qr - qv)

    # Field of wind
    # wind_vel = windfield(t, xv)
    wind_vel = (0,0)

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

    # Render text using TeX interpreter
    # plt.rc('text', usetex=True)

    # Plot data
    f = plt.figure(1)
    f.clear()

    # plt.plot(simdata['t'], np.sqrt(u**2 + w**2), marker='o')
    plt.plot(simdata['x'], simdata['z'], marker='o',
             label='Position of a vehicle in vehicle-carried frame')
    plt.plot(simdata['xr'], simdata['zr'],
             label='Reference trajectory')
    plt.xlabel('x coordinate')
    plt.ylabel('z coordinate')
    plt.grid()
    f.axes[0].invert_yaxis()
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

    return simdata

if __name__ == '__main__':
    run_n_plot()

# simdata = simulation.Simulation(Model).run()

# # Render text using TeX interpreter
# # plt.rc('text', usetex=True)

# # Plot data
# f = plt.figure()

# # plt.plot(simdata['t'], np.sqrt(u**2 + w**2), marker='o')
# plt.plot(simdata['x'], -simdata['z'], marker='o',
#          label='Position of a vehicle in vehicle-carried frame')
# plt.plot(simdata['xr'], -simdata['zr'],
#          label='Reference trajectory')
# plt.xlabel('x coordinate')
# plt.ylabel('z coordinate')
# plt.grid()
# f.axes[0].legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
#                  ncol=3, fancybox=True, shadow=True)

# f = plt.figure()
# # plt.plot(simdata['t'], simdata['z'], marker='o')
# u = simdata['u']
# w = simdata['w']
# plt.plot(simdata['t'], simdata['u'], label='$u(t)$')
# plt.plot(simdata['t'], simdata['w'], label='$w(t)$')
# plt.plot(simdata['t'], np.sqrt(u**2 + w**2), label=r'$\mathrm{TAS}(t)$')
# plt.xlabel('t')
# plt.ylabel(r'$u(t), w(t), \mathrm{TAS}(t)$')
# f.axes[0].legend()
# plt.grid()

# f = plt.figure()
# plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
# plt.plot(simdata['t'], np.rad2deg(simdata['theta']),
#          label=r"$\Theta(t)$")
# plt.step(simdata['t'], np.rad2deg(simdata['tr']), label=r"$\theta_r(t)$")
# plt.xlabel('t')
# plt.ylabel(r'$\alpha(t), \Theta(t)$')
# f.axes[0].legend()
# plt.grid()


# f = plt.figure()
# plt.plot(simdata['t'], np.rad2deg(np.arctan(w / u)), label=r"$\alpha(t)$")
# plt.plot(simdata['t'], np.rad2deg(simdata['q']),
#          label=r"$q(t)$")
# plt.step(simdata['t'], np.rad2deg(simdata['qr']), label=r"$q_r(t)$")
# plt.xlabel('t')
# plt.ylabel(r'$\alpha(t), q(t)$')
# f.axes[0].legend()
# plt.grid()
# plt.show()
