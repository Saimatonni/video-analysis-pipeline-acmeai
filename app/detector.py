from abc import ABC, abstractmethod

import cv2
import numpy as np
from shapely.geometry import Polygon


class FieldDetector(ABC):
    @abstractmethod
    def detect(
        self,
        frame: np.ndarray,
    ):
        raise NotImplementedError


class SyntheticFieldDetector(FieldDetector):

    def __init__(self, min_area: float):
        self.min_area = min_area

    def detect(self, frame):
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV,)
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        mask = cv2.inRange(hsv,lower_green,upper_green,)

        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE,)

        if not contours:
            return None

        largest = max(contours,key=cv2.contourArea,)

        if (
            cv2.contourArea(largest)
            <= self.min_area
        ):
            return None

        points = largest.reshape(
            -1,
            2,
        )

        if len(points) < 3:
            return None

        polygon = Polygon(points)

        if not polygon.is_valid:
            return None

        return polygon