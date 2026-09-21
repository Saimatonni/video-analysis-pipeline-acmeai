# Decisions 

## 1. Initial Code Review and Problem Identification

I started by reading and understanding the provided prototype manually rather than immediately rewriting it.

The initial prototype had several issues that I identified from the assignment requirements:

* The configuration was a raw Python dictionary.
* Every frame was processed, even when full-frame analysis was unnecessary.
* Expensive calculations could be repeated unnecessarily.
* Detection failures could be silently swallowed.
* Invalid detections were not explicitly represented or counted.
* Logging and operational observability were limited.
* The reporting API was not integrated into the pipeline.
* Reporting and processing failures were not clearly separated.


I also inspected the synthetic video generator separately to understand what kind of input the detector was actually receiving.

One important issue I identified during this process was that the generator creates a green field with **white pitch boundaries**, while the original detector was detecting the green region. Therefore, the detector and the generated test data were mismatched.

I kept the synthetic generator unchanged because the generator itself was useful for testing noisy and invalid input. Instead, I corrected the detector to match the actual characteristics of the generated video.

---

## 2. Separating the Original Code

My first implementation step was to manually identify the responsibilities inside the original script.

I separated the code into different components instead of keeping everything inside `synthetic_field_prototype.py`.

The main responsibilities became:

* `config.py` — configuration validation
* `models.py` — validated data structures
* `detector.py` — field detection
* `processor.py` — video processing
* `reporter.py` — communication with the reporting API
* `logging_config.py` — logging configuration

The intention was not to introduce unnecessary abstraction. I wanted each part to have a clear responsibility while keeping the overall system understandable.


---

## 3. Configuration Validation

### Problem

The original application used a dictionary such as:

```python
CONFIG = {
    "video_path": "...",
    "target_fps": 30,
    ...
}
```

This allowed missing, incorrectly typed, or invalid values to reach the processing stage.

### Decision

I introduced Pydantic configuration models.

The configuration is now validated when it is loaded rather than allowing an invalid value to fail somewhere during processing.

For example:

* `target_fps` must be greater than zero.
* `confidence_threshold` must be between 0 and 1.
* `min_area` must be greater than zero.
* Required nested configuration sections must exist.

I chose strict validation instead of silently falling back to defaults because this is a batch-processing pipeline where an invalid configuration should be detected before an unattended job starts.

---

## 4. Detector Abstraction

### Problem

The original `FieldBoundaryAnalyzer` directly contained the field detection logic.

The assignment states that the field-detection mechanism can vary between sports and deployments.

### Decision

I introduced a `FieldDetector` abstraction and moved the current implementation into `SyntheticFieldDetector`.

The processor now depends on the detector interface rather than knowing how the field is detected.

This gives the pipeline a clear seam where another detector implementation can be introduced later without rewriting the video-processing flow.

---

## 5. Synthetic Video / Detector Mismatch

During manual inspection of the supplied synthetic generator, I noticed that the generated video contains:

* a green background representing the field,
* white pitch boundary lines,
* occasional blank frames,
* occasional frames without a boundary,
* occasional small white noise shapes.

The original detector searched for green pixels. This could result in detecting the green field itself rather than the actual pitch boundary.

### Decision

I kept the synthetic generator as supplied because its noisy cases are useful for testing robustness.

Instead, I modified the detector to identify the white boundary.

---

## 6. Processing Efficiency

### Problem

The original implementation attempted detection on every frame.

For a long continuous video, this means expensive analysis is performed even when it is not necessary.

### Decision

I introduced configurable frame sampling based on the source video's FPS and the configured target analysis FPS.

For example, if the source video is 30 FPS and the configured analysis rate is 5 FPS, the detector is called approximately once every six frames.

This reduces the number of expensive detection operations while preserving the original video stream.

I also removed the artificial `time.sleep()` from the prototype because it was only simulating processing latency and should not exist in the production-oriented implementation.


---



## 7. Handling Invalid and Noisy Detections

### Problem

Real video can contain frames where the field boundary is:

* missing,
* partially obscured,
* too small,
* invalid,
* or incorrectly detected.

These cases should not crash the complete batch.

### Decision

The detector returns either a validated `Detection` object or `None`.

A detection is accepted only when it passes the required validation checks.

Invalid detections are counted separately rather than being inserted into the valid results as an area of zero.

The final average is calculated only from valid detections.

If there are no valid detections, the average is represented as `None` instead of incorrectly reporting zero.

This keeps invalid observations from polluting the calculated metrics.

---


## 8. Logging and Observability

### Problem

The original prototype mainly used `print()` statements and silently ignored exceptions in some places.

That is not sufficient for an unattended batch pipeline.

### Decision

I replaced important operational output with structured logging.

The pipeline records information such as:

* run ID,
* input video,
* source FPS,
* target analysis FPS,
* number of processed frames,
* number of valid detections,
* number of invalid detections,
* calculated results,
* reporting failures.

I also removed silent exception swallowing.

---

## 9. Reporting Service

### Problem

The assignment requires progress/outcome information to be sent to `mock_api` over the network.

The reporting service must not depend on shared files or a shared database.

### Decision

I introduced a dedicated `Reporter` component.

The pipeline reports events such as:

* `started`
* `completed`
* `failed`

The reporter communicates with the mock API over HTTP.

The reporting payloads are represented using validated models rather than constructing arbitrary dictionaries throughout the processing code.

---



## 10. Docker and Service Networking

The final structure uses Docker Compose with two services:

* `mock_api`
* `runner`

The runner communicates with the API using the Compose service name:

```text
http://mock_api:5000
```

rather than `localhost`.

This is important because `localhost` inside the runner container refers to the runner container itself, not the mock API container.


---


# AI / LLM Usage Disclosure

I used AI/LLM tools as an assistance tool during this assignment, but I did not rely on them to independently design, execute, or submit the solution without review.

I first manually inspected the provided prototype, identified the existing responsibilities and problems, and understood the assignment requirements. I then structured the original code into separate components and worked through the requirements incrementally.

For implementation, I used an LLM mainly as a coding/review assistant. For example, I asked questions/prompts similar to:

> "Here is the existing processor code and the assignment requirements. How can I separate the core processing logic from the runner while keeping the current behavior unchanged?"

Another example was:

> "The synthetic generator creates a green field with white pitch boundary lines, but my detector currently detects green pixels. Identify the mismatch and suggest a minimal change to the detector without changing the generator."

I also used the LLM to discuss implementation approaches for configuration validation, frame sampling, failure handling, logging, reporting, Docker Compose networking, and testing.

I reviewed the generated suggestions, adapted them to the project structure, ran the code locally, checked the results, and made corrections where necessary. 

I also used ChatGPT to help structure and polish this `DECISIONS.md` document and the final submission PDF. Grammarly was used for grammar and language correction.


---





## Running Locally

First start the mock API:

```bash
python mock_api/app.py
```

Then, in another terminal:

```bash
python synthetic_field_prototype.py
```

## Running with Docker

```bash
docker compose up --build
```

The Compose setup runs:

* `mock_api`
* `runner`

The runner communicates with the API using:

```text
http://mock_api:4000
```

## Limitations / Next Steps

This is intentionally a focused implementation rather than a complete production system.

With more time, I would:

* Add more automated tests.
* Add periodic progress reporting.
* Improve frame access/decoding efficiency for very long videos.
* Expand the detector implementations for different sports/deployments.



## GitHub

https://github.com/Saimatonni/video-analysis-pipeline-acmeai


