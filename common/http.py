"""Shared HTTP helper used by every skill script, so timeout and error handling stay consistent."""
import time

import requests

DEFAULT_TIMEOUT = 10

# Some public APIs (confirmed: Overpass) reject the default python-requests
# user agent as anti-scraping protection (HTTP 406), even though curl's default
# UA is accepted. Identify ourselves explicitly to avoid that.
HEADERS = {"User-Agent": "secours-inondations-plugin/0.1 (Claude Code skill)"}

# Public instances of APIs like Overpass rate-limit bursts of requests (HTTP 429).
# A skill that fires several queries per call (e.g. localisation's "acces") hits this
# in practice, confirmed while building it, so retry those (and transient 5xx) with
# backoff instead of failing outright. Other 4xx (bad params) fail immediately.
RETRYABLE_STATUS_CODES = {429, 502, 503, 504}
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def get_json(url, params=None, timeout=DEFAULT_TIMEOUT):
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=timeout, headers=HEADERS)
            if response.status_code in RETRYABLE_STATUS_CODES and attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))
                continue
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            return {"error": f"{type(exc).__name__}: {exc}"}
    return {"error": "trop de requetes, reessayer plus tard (429 persistant)"}
