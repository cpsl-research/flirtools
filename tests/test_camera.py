import logging

import PySpin

from flirtools.camera import camera_from_config_file


def test_flir_camera_init():
    config = "config/north-building-four-cameras/camera-1.yaml"
    try:
        camera = camera_from_config_file(config)
    except PySpin.SpinnakerException as e:
        logging.warning("WARNING: could not successfully connect to camera")
        logging.warning(e)
    else:
        camera.destroy()


def test_flir_camera_get_singleframe():
    config = "config/north-building-four-cameras/camera-1.yaml"
    try:
        camera = camera_from_config_file(config)
    except PySpin.SpinnakerException as e:
        logging.warning("WARNING: could not successfully connect to camera")
        logging.warning(e)
    else:
        try:
            img = camera.get_singleframe()
            assert img.shape[0] == camera.calib.intrinsics.height
            assert img.shape[1] == camera.calib.intrinsics.width
        finally:
            camera.destroy()


def test_flir_camera_get_multiframe():
    config = "config/north-building-four-cameras/camera-1.yaml"
    try:
        camera = camera_from_config_file(config)
    except PySpin.SpinnakerException as e:
        logging.warning("WARNING: could not successfully connect to camera")
        logging.warning(e)
    else:
        try:
            dt = 2.0
            img_sequence = camera.get_multiframe(dt=dt)
            assert img_sequence.shape[0] == int(dt * camera.config["fps"])
            assert img_sequence.shape[1] == camera.calib.intrinsics.height
            assert img_sequence.shape[2] == camera.calib.intrinsics.width
        finally:
            camera.destroy()


def test_flir_camera_get_multiframe_from_continuous():
    config = "config/north-building-four-cameras/camera-1.yaml"
    try:
        camera = camera_from_config_file(config)
    except PySpin.SpinnakerException as e:
        logging.warning("WARNING: could not successfully connect to camera")
        logging.warning(e)
    else:
        try:
            dt = 2.0
            img_sequence = camera.get_multiframe_from_continuous(dt=dt)
            assert img_sequence.shape[0] == int(dt * camera.config["fps"])
            assert img_sequence.shape[1] == camera.calib.intrinsics.height
            assert img_sequence.shape[2] == camera.calib.intrinsics.width
        finally:
            camera.destroy()
