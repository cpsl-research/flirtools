import numpy as np
import yaml

from .utils import q_mult_vec, transform_orientation


def calibration_from_config_file(config_file):
    with open(config_file) as stream:
        config = yaml.safe_load(stream)
    return calibration_from_config(config)


def calibration_from_config(config):
    intr = Intrinsics(**config["calibration"]["intrinsics"])
    extr = Extrinsics(**config["calibration"]["extrinsics"])
    return Calibration(config["calibration"]["channel_order"], intr, extr)


class Intrinsics:
    __slots__ = "width", "height", "f", "P"

    def __init__(
        self, width: int, height: int, f: float, sx: float, sy: float, g: float
    ) -> None:
        self.width = width
        self.height = height
        self.f = f
        mx = self.width / sx
        my = self.height / sy
        self.P = np.array(
            [
                [self.f * mx, g, self.width / 2, 0],
                [0, self.f * my, self.height / 2, 0],
                [0, 0, 1, 0],
            ]
        )


class Extrinsics:
    __slots__ = "x", "q", "T"

    def __init__(
        self,
        dx: float = 0.0,
        dy: float = 0.0,
        dz: float = 0.0,
        qw: float = 1.0,
        qx: float = 0.0,
        qy: float = 0.0,
        qz: float = 0.0,
    ) -> None:
        self.x = np.array([dx, dy, dz])
        self.q = np.quaternion(qw, qx, qy, qz)
        R = transform_orientation(self.q.conjugate(), "quat", "DCM", n_prec=6)
        t = np.reshape(q_mult_vec(self.q.conjugate(), -self.x, n_prec=6), (3, 1))
        self.T = np.block([[R, t], [np.zeros((1, 3)), np.ones((1, 1))]])


class Calibration:
    def __init__(
        self, channel_order: str, intrinsics: Intrinsics, extrinsics: Extrinsics
    ):
        self.channel_order = channel_order
        self.intrinsics = intrinsics
        self.extrinsics = extrinsics

        # full matrix for converting coordinates
        self.M = self.intrinsics.P @ self.extrinsics.T
