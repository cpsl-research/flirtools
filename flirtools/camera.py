import cv2
import numpy as np
import PySpin
import yaml

from .calibration import calibration_from_config


def camera_from_config_file(config_file):
    with open(config_file) as stream:
        config = yaml.safe_load(stream)
    return camera_from_config(config)


def camera_from_config(config):
    return Camera(config)


def ptr_to_image(ptr, img_dimensions) -> np.ndarray:
    img = np.frombuffer(ptr.GetData(), dtype=np.uint8).reshape(
        (img_dimensions[1], img_dimensions[0])
    )
    img = cv2.cvtColor(img, cv2.COLOR_BayerBG2BGR)
    return img


class Camera:
    def __init__(self, config: dict, writable: bool = True) -> None:
        self.config = config
        self.calib = calibration_from_config(config["calibration"])
        self.streaming = False
        self.image_dimensions = (
            self.calib.intrinsics.width,
            self.calib.intrinsics.height,
        )
        self.handle = None
        self.system = None
        self.serial = None
        self.writable = writable
        self.initialize()

    def initialize(self):
        self.system = PySpin.System.GetInstance()
        cam_list = self.system.GetCameras()
        i_att = 0
        while len(cam_list) > 0:
            self.handle = cam_list.GetBySerial(self.config["serial"])
            try:
                self.handle.Init()
                print(
                    f"Successfully connected to {self.config['model']} via serial number",
                )
                break
            except PySpin.SpinnakerException:
                cam_list.RemoveBySerial(self.config["serial"])
                i_att += 1
                if i_att > 10:
                    raise RuntimeError(
                        f"Unable to connect to {self.config.model} via serial number"
                    )
        self.serial = self.config["serial"]
        cam_list.Clear()
        del cam_list

        # Set the camera properties here
        if self.writable:
            self.handle.Width.SetValue(self.image_dimensions[0])
            self.handle.Height.SetValue(self.image_dimensions[1])
            self.handle.AcquisitionFrameRateEnable.SetValue(
                True
            )  # enable changes to FPS
            self.handle.AcquisitionFrameRate.SetValue(
                self.config["fps"]
            )  # max is 24fps for FLIR BFS

    def deinitialize(self):
        self.serial = None
        if self.handle is not None:
            self.handle.DeInit()
            del self.handle
            self.handle = None
        if self.system is not None:
            self.system.ReleaseInstance()
            del self.system
            self.system = None

    def destroy(self):
        print(f"Destroying camera {self.serial} instance...", end="")
        self.deinitialize()
        print("done")

    def get_singleframe(self) -> np.ndarray:
        self.handle.AcquisitionMode.SetValue(PySpin.AcquisitionMode_SingleFrame)
        self.handle.BeginAcquisition()
        try:
            ptr = self.handle.GetNextImage()
        except PySpin.SpinnakerException as e:
            raise e
        img = ptr_to_image(ptr, self.image_dimensions)
        ptr.Release()
        self.handle.EndAcquisition()
        return img

    def get_multiframe(self, dt: float) -> np.ndarray:
        """NOTE: we do not recommend using this due to incomplete frames

        Instead, we recommend multiframe from continuous
        """
        n_frames = int(dt * self.config["fps"])
        self.handle.AcquisitionMode.SetValue(PySpin.AcquisitionMode_MultiFrame)
        self.handle.AcquisitionFrameCount.SetValue(n_frames)
        self.handle.BeginAcquisition()
        images = []
        for _ in range(n_frames):
            try:
                ptr = self.handle.GetNextImage(500)  # why such a high timeout...
            except PySpin.SpinnakerException as e:
                raise e  # done with acquisition
            img = ptr_to_image(ptr, self.image_dimensions)
            images.append(img)
            ptr.Release()
        self.handle.EndAcquisition()
        return np.array(images)

    def get_multiframe_from_continuous(self, dt: float) -> np.ndarray:
        n_frames = int(dt * self.config["fps"])
        self.handle.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.handle.BeginAcquisition()
        images = []
        while True:
            try:
                ptr = self.handle.GetNextImage(50)
            except PySpin.SpinnakerException:
                continue
            if ptr.IsIncomplete():
                continue  # discard image
            img = ptr_to_image(ptr, self.image_dimensions)
            images.append(img)
            ptr.Release()
            if len(images) >= n_frames:
                break
        self.handle.EndAcquisition()
        return np.array(images)
