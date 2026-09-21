import logging
import time

import requests

from app.models import (
    JobEvent,
    ProgressReport,
)


logger = logging.getLogger(__name__)


class Reporter:

    def __init__(
        self,
        base_url: str,
        timeout: float = 3,
        retries: int = 2,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

    def _post(self,path: str,payload,):

        url = (f"{self.base_url}{path}")

        for attempt in range(
            self.retries + 1
        ):

            try:

                response = requests.post(
                    url,
                    json=payload.model_dump(mode="json"),
                    timeout=self.timeout,
                )

                response.raise_for_status()

                return

            except requests.RequestException as exc:

                logger.warning(
                    "Reporting attempt %d failed: %s",
                     attempt + 1,
                     exc,
                )

                if (
                    attempt
                    < self.retries
                ):
                    time.sleep(0.5)

        raise RuntimeError(
            "Reporting failed"
        )

    def report_progress(
        self,
        report: ProgressReport,
    ):
        self._post("/api/v1/jobs/progress",report,)

    def report_event(
        self,
        event: JobEvent,
    ):
        self._post("/api/v1/jobs/events",event,)