import cv2
import numpy as np


def cycle_through_images(img_sequence: np.ndarray, delay: float = 0.1):
    height = 960
    i = 0
    while True:
        idx = i % img_sequence.shape[0]
        img = img_sequence[idx]
        img = cv2.resize(img, (int(height * img.shape[1] / img.shape[0]), height))
        font = cv2.FONT_HERSHEY_SIMPLEX
        bottomLeftCornerOfText = (10, 500)
        fontScale = 5
        fontColor = (255, 255, 255)
        thickness = 15
        lineType = 2

        cv2.putText(
            img,
            f"Image {idx}",
            bottomLeftCornerOfText,
            font,
            fontScale,
            fontColor,
            thickness,
            lineType,
        )

        cv2.imshow(f"image", img)
        cv2.waitKey(int(delay * 1000))
        i += 1
