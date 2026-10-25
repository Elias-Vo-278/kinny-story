"""Small bounded, sequential client. No arbitrary URLs from source metadata."""
import json
import os
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler

ALLOWED_HOSTS = {'gutendex.com', 'gutenberg.pglaf.org', 'vi.wikisource.org'}


class SourceRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError('Unexpected redirect outside allowed HTTPS sources')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def retry_delay(value, attempt):
    try:
        return min(60, max(0, float(value)))
    except (TypeError, ValueError):
        try:
            return min(60, max(0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()))
        except (TypeError, ValueError):
            return 2 ** attempt


class Client:
    def __init__(self):
        self.last_request = 0

    def get(self, url, as_json=True):
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS:
            raise ValueError('Source URL is outside the allowed HTTPS hosts')
        for attempt in range(3):
            time.sleep(max(0, float(os.getenv('REQUEST_DELAY', '2')) - (time.monotonic() - self.last_request)))
            try:
                self.last_request = time.monotonic()
                request = Request(url, headers={'User-Agent': os.getenv('IMPORT_USER_AGENT', 'KinnyStoryLocal/0.1 (local development)')})
                with build_opener(SourceRedirects()).open(request, timeout=30) as response:
                    if urlsplit(response.url).hostname not in ALLOWED_HOSTS:
                        raise ValueError('Unexpected redirect host')
                    body = response.read(20_000_001)
                    if len(body) > 20_000_000:
                        raise ValueError('Source document exceeds 20 MB')
                    result = body.decode('utf-8-sig')
                    if not as_json:
                        return result
                    data = json.loads(result)
                    if 'error' in data:
                        if data['error'].get('code') in ('maxlag', 'ratelimited') and attempt < 2:
                            time.sleep(2 ** (attempt + 1))
                            continue
                        raise ValueError(f"Source API error: {data['error']}")
                    return data
            except HTTPError as error:
                if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                    raise
                time.sleep(retry_delay(error.headers.get('Retry-After'), attempt))
            except (URLError, TimeoutError):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError('Request attempts exhausted')
