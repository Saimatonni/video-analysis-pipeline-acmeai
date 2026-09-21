import time
import cv2
import numpy as np
from shapely.geometry import Polygon
import logging
from app.config import PipelineConfig

logger = logging.getLogger(__name__)
class FieldBoundaryAnalyzer:
    # def __init__(self, config: dict):
    #     self.config = config
    #     self.sport = config.get("field_detector", {}).get("sport", "soccer")
    #     self.threshold = config.get("confidence_threshold", 0.5)
    def __init__(
        self,
        config: PipelineConfig,
        detector
    ):
        self.config = config
        self.detector = detector
        self.sport = (
            config.field_detector.sport
        )
        self.threshold = (
            config.confidence_threshold
        )

    def process_video(self, video_path: str):
        print(f"Starting processing for video: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
      
        if not cap.isOpened():
            print("Error: Could not open video stream.")
            return
        
        source_fps = cap.get(cv2.CAP_PROP_FPS)
        if source_fps <= 0:
           raise RuntimeError("Unable to determine source FPS")
        
        sample_interval = max(1,round(source_fps / self.config.target_fps))


        frame_count = 0
        invalid_detections = 0
        detections = []
        # detected_polygons = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if (frame_count - 1) % sample_interval != 0:
              continue

            # mask = self._extract_mask(frame)
            # poly = self._derive_polygon_from_mask(mask)

            try:
                detection = self.detector.detect(frame,frame_count,)
            except Exception:
               logger.exception("Detector failed at frame %d",frame_count,)
               invalid_detections += 1
               continue
            if detection is None:
                invalid_detections += 1
                continue

            detections.append(detection)
            # poly = self.detector.detect(frame)

            # if poly and poly.is_valid:
            #     outer_boundary = Polygon([(0, 0), (1280, 0), (1280, 720), (0, 720)])
            #     intersection_area = poly.intersection(outer_boundary).area
            #     detected_polygons.append((frame_count, poly, intersection_area))

            # Simulate heavy per-frame processing latency
            # time.sleep(0.005)

        cap.release()
        average_area = (sum(d.area for d in detections)
          / len(detections)
          if detections
          else None
        )
        # print(f"Processed {frame_count} frames. Found {len(detected_polygons)} boundaries.")
        # return detected_polygons
        print(f"Processed {frame_count} frames.")
        print(f"Valid detections: {len(detections)}")
        print(f"Invalid detections: {invalid_detections}")
        print(f"Average area: {average_area}")
        return detections