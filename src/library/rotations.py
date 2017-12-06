import numpy as np

from numpy import cos, sin


def Rbv(phi, theta, psi):
    """Rbv(phi, theta, psi):

    Return the total rotation matrix transforming the vector
    coordinates in vehicle-carried vertical axes to the body axes.

    Parameters
    ----------
    phi : float
        Bank angle (rad).
    theta : float
        Pitch (or elevation) angle (rad).
    psi : float
        Yaw (or azimuth) angle (rad)

    Returns
    -------
    out : ndarray
        the total rotation matrix transforming the vector coordinates
        in vehicle-carried vertical axes to the body axes


    Notes
    -----

    Additionaly the function checks whether theta, phi and psi values
    are inside the plausible range. In this way it is also able to
    detect if any of the angles is expressed in degrees.

    To apply the inverse transformation, i.e. from the body axes to
    the vehicle-carried vertical axes, the output array should be
    transposed.

    """

    phi_min, phi_max = (-np.pi, np.pi)
    theta_min, theta_max = (-np.pi/2, np.pi/2)
    psi_min, psi_max = (0, 2 * np.pi)

    if not (theta_min <= theta <= theta_max):
        raise ValueError('Theta value is not inside correct range')
    elif not (phi_min <= phi <= phi_max):
        raise ValueError('Phi value is not inside correct range')
    elif not (psi_min <= psi <= psi_max):
        raise ValueError('Psi value is not inside correct range')

    return np.array([
        [cos(theta) * cos(psi),
         cos(theta) * sin(psi),
         -sin(theta)],
        [sin(phi) * sin(theta) * cos(psi) - cos(phi) * sin(psi),
         sin(phi) * sin(theta) * sin(psi) + cos(phi) * cos(psi),
         sin(phi) * cos(theta)],
        [cos(phi) * sin(theta) * cos(psi) + sin(phi) * sin(psi),
         cos(phi) * sin(theta) * sin(psi) - sin(phi) * cos(psi),
         cos(phi) * cos(theta)]
    ])


def Rbs(alpha, beta):
    """Rbs(alpha, beta)

    Return the total rotation matrix transforming the vector
    coordinates in the stability axes frame of reference to the body
    axes.

    """

    alpha_min, alpha_max = (-np.pi/2, np.pi/2)
    beta_min, beta_max = (-np.pi, np.pi)

    if not (alpha_min <= alpha <= alpha_max):
        raise ValueError('Alpha value is not inside correct range')
    elif not (beta_min <= beta <= beta_max):
        raise ValueError('Beta value is not inside correct range')

    # Transformation matrix from body to wind
    return np.array([
        [cos(alpha) * cos(beta),
         - cos(alpha) * sin(beta),
         -sin(alpha)],
        [sin(beta),
         cos(beta),
         0],
        [sin(alpha) * cos(beta),
         -sin(alpha) * sin(beta),
         cos(alpha)]
    ])
