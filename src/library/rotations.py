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

    # this reduces run time by about 30% (sic!!)
    s_phi = sin(phi)
    c_phi = cos(phi)

    s_th = sin(theta)
    c_th = cos(theta)

    s_psi = sin(psi)
    c_psi = cos(psi)

    return np.array([
        [c_th * c_psi,
         c_th * s_psi,
         -s_th],
        [s_phi * s_th * c_psi - c_phi * s_psi,
         s_phi * s_th * s_psi + c_phi * c_psi,
         s_phi * c_th],
        [c_phi * s_th * c_psi + s_phi * s_psi,
         c_phi * s_th * s_psi - s_phi * c_psi,
         c_phi * c_th]
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

    # this reduces run time by another 10% (sic!!)
    s_alpha = sin(alpha)
    c_alpha = cos(alpha)
    s_beta  = sin(beta)
    c_beta  = cos(beta)

    # Transformation matrix from body to wind
    return np.array([
        [c_alpha * c_beta,
         - c_alpha * s_beta,
         -s_alpha],
        [s_beta,
         c_beta,
         0],
        [s_alpha * c_beta,
         -s_alpha * s_beta,
         c_alpha]
    ])
