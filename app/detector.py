from abc import ABC, abstractmethod

import cv2
import numpy as np
from shapely.geometry import Polygon
from app.models import Detection


class FieldDetector(ABC):

    @abstractmethod
    def detect(
        self,
        frame: np.ndarray,
        frame_number: int,
    ) -> Detection | None:
        raise NotImplementedError


class SyntheticFieldDetector(FieldDetector):

    def __init__(self, min_area: float):
        self.min_area = min_area

    def detect(self,frame: np.ndarray,frame_number: int,) -> Detection | None:

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV,)

        lower_white = np.array([0, 0, 180])
        upper_white = np.array([180, 80, 255])

        # mask = cv2.inRange(hsv,lower_green,upper_green,)
        mask = cv2.inRange(
            hsv,
            lower_white,
            upper_white,
        )

        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE,)

        if not contours:
            return None

        largest = max(contours,key=cv2.contourArea,)

        area = cv2.contourArea(largest)

        if area <= self.min_area:
            return None

        points = largest.reshape(-1, 2)

        if len(points) < 3:
            return None

        polygon = Polygon(points)

        if not polygon.is_valid:
            return None

        return Detection(frame_number=frame_number,area=area,)