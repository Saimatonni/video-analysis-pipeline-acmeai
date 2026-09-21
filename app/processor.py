import time
import cv2
import numpy as np
from shapely.geometry import Polygon
import logging
from app.config import PipelineConfig
import uuid

from app.models import (
    JobEvent,
    ProgressReport,
)
from app.reporter import Reporter

logger = logging.getLogger(__name__)
class FieldBoundaryAnalyzer:
    def __init__(
        self,
        config: PipelineConfig,
        detector,
        reporter: Reporter,
    ):
        self.config = config
        self.detector = detector
        self.reporter = reporter
        self.sport = (
            config.field_detector.sport
        )
        self.threshold = (
            config.confidence_threshold
        )

    def process_video(self, video_path: str):
        # print(f"Starting processing for video: {video_path}")
        run_id = str(uuid.uuid4())
        logger.info("Starting processing: run_id=%s video=%s",run_id,video_path,)
        # pipeline start
        try:
            self.reporter.report_event(
                JobEvent(
                    run_id=run_id,
                    event="started",
                    message="Pipeline started",
                )
            )
        except Exception:
            logger.exception(
                "Failed to report pipeline start: run_id=%s",
                run_id,
            )
        
        cap = cv2.VideoCapture(video_path)
      
        if not cap.isOpened():
            logger.error(
                "Could not open video stream: %s",
                video_path,
            )
            try:
                self.reporter.report_event(
                    JobEvent(
                        run_id=run_id,
                        event="failed",
                        message="Could not open video stream",
                    )
                )
            except Exception:
                logger.exception(
                    "Failed to report pipeline failure: "
                    "run_id=%s",
                    run_id,
                )

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

        cap.release()
        average_area = (sum(d.area for d in detections)
          / len(detections)
          if detections
          else None
        )
        # print(f"Processed {frame_count} frames. Found {len(detected_polygons)} boundaries.")
        # return detected_polygons
        try:
             self.reporter.report_event(
                JobEvent(
                    run_id=run_id,
                    event="completed",
                    message="Pipeline completed",
                )
            )

        except Exception:
            logger.exception(
                "Failed to report pipeline completion: "
                "run_id=%s",
                run_id,
            )
        print(f"Processed {frame_count} frames.")
        print(f"Valid detections: {len(detections)}")
        print(f"Invalid detections: {invalid_detections}")
        print(f"Average area: {average_area}")
        
        return detections