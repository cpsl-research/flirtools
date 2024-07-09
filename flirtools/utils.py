import numpy as np
import quaternion


# from numba import jit
# from numba.types import float64, int64


def q_mult_vec(q, v, n_prec=None):
    """
    v' = v + 2 * r x (s * v + r x v) / m
    where x represents the cross product, s and r are the scalar and vector parts
    of the quaternion, respectively, and m is the sum of the squares of the
    components of the quaternion.
    """
    try:
        q = q.q  # if input is a Rotation
    except AttributeError:
        pass
    s = q.w
    r = q.vec
    m = q.w**2 + q.x**2 + q.y**2 + q.z**2
    try:
        v2x = _q_mult_vec(s, r, m, v.x)
        if n_prec is not None:
            v2x = np.round(v2x, n_prec)
        return v.factory()(v2x, v.reference)
    except AttributeError:
        v2x = _q_mult_vec(s, r, m, v)
        if n_prec is not None:
            v2x = np.round(v2x, n_prec)
        return v2x


# @jit(nopython=True, fastmath=False)
def _q_mult_vec(s, r, m, v):
    return v + 2 * np.cross(r, (s * v + np.cross(r, v))) / m


# @jit(float64[:](float64[:], int64, float64[:]), nopython=True)
def fastround(arr, ndec, out):
    for i in range(len(arr)):
        if np.abs(arr[i]) < 1e-12:
            arr[i] = 0.0
    return np.round_(arr, ndec, out)


# @jit(nopython=True, fastmath=True)
def _make_DCM(euler):
    R = float(euler[0])
    P = float(euler[1])
    Y = float(euler[2])
    # This is DCM of global level --> body
    DCM = np.array(
        [
            [
                np.cos(P) * np.cos(Y),
                np.sin(R) * np.sin(P) * np.cos(Y) - np.cos(R) * np.sin(Y),
                np.cos(R) * np.sin(P) * np.cos(Y) + np.sin(R) * np.sin(Y),
            ],
            [
                np.cos(P) * np.sin(Y),
                np.sin(R) * np.sin(P) * np.sin(Y) + np.cos(R) * np.cos(Y),
                np.cos(R) * np.sin(P) * np.sin(Y) - np.sin(R) * np.cos(Y),
            ],
            [-np.sin(P), np.sin(R) * np.cos(P), np.cos(R) * np.cos(P)],
        ]
    )
    return DCM.T


def euler_to_R(euler: np.ndarray):
    """
    Convert angles to direction cosine matrix

    :euler - tuple of (roll, pitch, yaw) / (phi, theta, psi) angles - generally will be
             angles from the local frame to the body

    output will generally be R_global_to_body (e.g., R_ned_to_body)
    assumes R = Rx(phi) * Ry(theta) * Rz(psi)
    where - phi on [-pi, pi] (roll)
          - theta on [-pi/2, pi/2] (pitch)
          - psi on [-pi, pi] (yaw/heading)

    could also get this by composing individual axis rotations in sequence, but
    explicitly writing it out is more efficient
    """
    if len(euler.shape) == 1:
        DCM = _make_DCM(euler)
    else:
        DCM = np.zeros((3, 3, euler.shape[1]), dtype=float)
        for i in range(euler.shape[1]):
            DCM[:, :, i] = _make_DCM(euler[:, i])

    return DCM


def transform_orientation(x, a_from, a_to, n_prec=None):
    """
    Transform angles from different representations
    eulers must be represented in (roll, pitch, yaw) order

    :x - vector or matrix describing the orientation
    :a_from - {'euler', 'quat', 'DCM'}
    :a_to - {'euler', 'quat', 'DCM'}
    """
    FROM = a_from.lower()
    TO = a_to.lower()

    q_list = ["quat", "quaternion"]
    e_list = ["euler"]
    d_list = ["dcm"]

    if isinstance(x, list) and len(x) == 3:
        x = np.asarray([float(xi) for xi in x])

    if FROM in e_list:
        if TO in q_list:
            DCM = euler_to_R(x)
            if len(DCM.shape) == 3:
                DCM = np.transpose(DCM, (2, 0, 1))
            x_out = quaternion.from_rotation_matrix(DCM)
        elif TO in d_list:
            x_out = euler_to_R(x)
        elif TO in e_list:
            x_out = x
        else:
            raise NotImplementedError
    elif FROM in q_list:
        if TO in d_list:
            x_out = quaternion.as_rotation_matrix(x)
            if len(x_out.shape) == 3:
                x_out = np.transpose(x_out, (1, 2, 0))
        elif TO in e_list:
            DCM = quaternion.as_rotation_matrix(x)
            if len(DCM.shape) == 3:
                DCM = np.transpose(DCM, (1, 2, 0))
            x_out = R_to_euler(DCM)
        elif TO in q_list:
            x_out = x
        else:
            raise NotImplementedError
    elif FROM in d_list:
        if TO in e_list:
            x_out = R_to_euler(x)
        elif TO in q_list:
            if len(x.shape) == 3:
                x = np.transpose(x, (2, 0, 1))
            x_out = quaternion.from_rotation_matrix(x)
        elif TO in d_list:
            x_out = x
        else:
            raise NotImplementedError
    else:
        raise NotImplementedError

    if TO in q_list:
        if x_out.w < 0:
            x_out *= -1

    # error checking
    if ((TO in q_list) and (np.isnan(x_out.w) or np.isnan(x_out.vec).any())) or (
        (TO not in q_list) and np.isnan(x_out).any()
    ):
        import pdb

        pdb.set_trace()
        raise RuntimeError(x_out)

    # rounding errors
    if n_prec is not None:
        x_out = np.round(x_out, n_prec)

    return x_out
