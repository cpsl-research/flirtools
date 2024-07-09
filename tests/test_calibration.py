import numpy as np

from flirtools.calibration import Calibration, calibration_from_config_file


def test_read_calibration_from_config():
    config = "config/example-flir-bfs-config.yaml"
    calib = calibration_from_config_file(config)
    assert isinstance(calib, Calibration)


def test_transform_coordinates():
    config = "config/example-flir-bfs-config.yaml"
    calib = calibration_from_config_file(config)

    pts_in_world = np.array([[1, 0, 0], [100, 0, 0], [0, 0, 1], [0, 1, 0], [1, 1, 1]]).T
    pts_in_world_homog = np.vstack((pts_in_world, np.ones((1, pts_in_world.shape[1]))))
    pts_in_cam = calib.M @ pts_in_world_homog
    pts_in_cam /= pts_in_cam[2, :]
    center = np.array([calib.intrinsics.width / 2, calib.intrinsics.height / 2])
    assert np.allclose(pts_in_cam[:2, 0], center)
    assert np.allclose(pts_in_cam[:2, 1], center)
