"""Client REST pour l'API externe v2 de Pennylane.

Lecture : get() / paginate().  Écriture : post() / put() (utilisées à partir de la Phase 2).
Gère l'authentification, la pagination par curseur, le throttling (4 req/s) et les erreurs.
"""
import json
import time
import uuid
import urllib.error
import urllib.parse
import urllib.request

from . import config


class PennylaneError(Exception):
    """Erreur renvoyée par l'API Pennylane (avec code HTTP et détail)."""


class PennylaneClient:
    def __init__(self, token=None, base_url=None, max_rps=4):
        self.token = token or config.get_token()
        if not self.token:
            raise PennylaneError(
                "Token Pennylane absent : pose PENNYLANE_API_TOKEN dans l'environnement "
                "(ou dans pennylane.env du répertoire TCIO_APIS_ENV_DIR)."
            )
        self.base_url = (base_url or config.BASE_URL).rstrip("/")
        self._min_interval = 1.0 / max_rps
        self._last_call = 0.0

    # --- interne ---
    def _throttle(self):
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _request(self, method, path, params=None, json_body=None, _retries=3):
        url = self.base_url + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        data = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Accept", "application/json")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        self._throttle()
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                body = resp.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            if e.code == 429 and _retries > 0:  # rate limit : on patiente et on retente
                time.sleep(1.5)
                return self._request(method, path, params, json_body, _retries - 1)
            detail = e.read().decode("utf-8", "ignore")[:500]
            raise PennylaneError(f"{method} {path} -> HTTP {e.code}: {detail}") from e
        except urllib.error.URLError as e:
            raise PennylaneError(f"{method} {path} -> {e}") from e

    # --- API publique ---
    def get(self, path, params=None):
        return self._request("GET", path, params=params)

    def post(self, path, json_body):
        return self._request("POST", path, json_body=json_body)

    def put(self, path, json_body):
        return self._request("PUT", path, json_body=json_body)

    def delete(self, path, params=None):
        return self._request("DELETE", path, params=params)

    def upload_file(self, file_bytes, filename, field="file", path="/file_attachments"):
        """Upload multipart d'un fichier (PDF) → renvoie le JSON (contenant l'id)."""
        boundary = "----pennylane" + uuid.uuid4().hex
        body = bytearray()
        body += f"--{boundary}\r\n".encode()
        body += (
            f'Content-Disposition: form-data; name="{field}"; filename="{filename}"\r\n'
        ).encode()
        body += b"Content-Type: application/pdf\r\n\r\n"
        body += file_bytes
        body += f"\r\n--{boundary}--\r\n".encode()
        req = urllib.request.Request(self.base_url + path, data=bytes(body), method="POST")
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
        req.add_header("Accept", "application/json")
        self._throttle()
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")[:500]
            raise PennylaneError(f"POST {path} (upload) -> HTTP {e.code}: {detail}") from e

    def me(self):
        return self.get("/me")

    def paginate(self, path, params=None, page_limit=None):
        """Itère sur tous les items d'un endpoint de liste (pagination par curseur)."""
        params = dict(params or {})
        params.setdefault("limit", 100)
        pages = 0
        while True:
            data = self.get(path, params=params)
            items = data.get("items") if isinstance(data, dict) else data
            for item in (items or []):
                yield item
            if not isinstance(data, dict) or not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break
            params["cursor"] = cursor
            pages += 1
            if page_limit and pages >= page_limit:
                break
