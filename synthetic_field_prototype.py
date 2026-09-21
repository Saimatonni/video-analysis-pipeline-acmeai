import os
from synthetic_generator import generate_synthetic_video
from app.processor import FieldBoundaryAnalyzer
from app.config import (
    CropSearchConfig,
    FieldDetectorConfig,
    PipelineConfig,
)
from app.detector import FieldDetector, SyntheticFieldDetector
from app.reporter import Reporter


CONFIG = PipelineConfig(
    video_path="synthetic_pitch_feed.mp4",
    target_fps=5,
    confidence_threshold=0.5,
    field_detector=FieldDetectorConfig(
        type="sam_mask_v1",
        sport="football",
        min_area=1000,
    ),
    crop_search=CropSearchConfig(
        aspect_ratio="16:9",
        padding_px=20,
    ),
    debug_mode=True,
)


def run_pipeline():
    # Helper to generate input file if it doesn't exist locally
    # generate_synthetic_video(CONFIG["video_path"])
    generate_synthetic_video(CONFIG.video_path)
    detector = SyntheticFieldDetector(CONFIG.field_detector.min_area)
    # reporter = Reporter(
    #     base_url="http://localhost:4000",
    # )
    reporter = Reporter(base_url=os.getenv("MOCK_API_URL","http://localhost:5000",),)
    analyzer = FieldBoundaryAnalyzer(CONFIG, detector, reporter)
    # results = analyzer.process_video(CONFIG["video_path"])
    results = analyzer.process_video(CONFIG.video_path)
    print(f"Pipeline finished with {len(results) if results else 0} results.")


if __name__ == "__main__":
    run_pipeline()
