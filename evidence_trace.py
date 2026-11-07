"""Private, integrity-checked evidence decision journal.

Audit records intentionally omit prompts, answer bodies, client IP addresses,
bearer tokens, and source file paths. The existing conversation log retains
full text under its existing privacy policy; this journal is metadata only.
A hash chain catches accidental modification/truncation of interior records.
It is NOT tamper-proof against a privileged actor rewriting the whole file.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import threading

SCHEMA = "iconic-evidence-audit-v1"
ZERO = "0" * 64
ALLOWED_STAGES = frozenset({
    "request.accepted", "evidence.retrieved", "routing.selected",
    "model.completed", "verification.completed", "response.completed",
    "response.failed", "web.consent.offered", "web.consent.decided",
    "verification.claim",
    "release.event",
})
ALLOWED_FIELDS = frozenset({
    "request_id", "workspace", "session_ref", "prompt_ref", "answer_ref",
    "intent", "retrieval", "source_count", "sources", "source_refs",
    "method", "claim_count", "supported_count", "needs_review_count",
    "failed_count", "invalid_citations", "numeric_warnings",
    "verifier_status", "model", "duration_ms", "result", "error_class",
    "release", "mode", "web_requested", "web_consent", "response_bytes",
    "audit_error", "attempt", "status", "claim_index", "claim_ref",
    "source_numbers", "reason", "quote_count", "quotes_matched",
})
PROHIBITED = {"question", "prompt", "answer", "body", "raw", "content", "token",
              "ip", "address", "cookie", "bearer", "key", "password", "path"}


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


class EvidenceJournal:
    def __init__(self, state_dir, release="unknown", filename="evidence-audit-v1.jsonl"):
        self.root = Path(state_dir).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.path = self.root / filename
        self.secret_path = self.root / "evidence-audit.key"
        self.lock = threading.RLock()
        self.release = str(release)[:64]
        self.secret = self._load_secret()
        self.sequence, self.previous = self.verify()

    def _load_secret(self):
        if not self.secret_path.is_file():
            key = secrets.token_bytes(32)
            try:
                fd = os.open(self.secret_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                try:
                    os.write(fd, key)
                    os.fsync(fd)
                finally:
                    os.close(fd)
            except FileExistsError:
                pass
        key = self.secret_path.read_bytes()
        if len(key) != 32:
            raise ValueError("Invalid evidence journal HMAC key")
        if self.secret_path.stat().st_mode & 0o077:
            os.chmod(self.secret_path, 0o600)
        return key

    def ref(self, value):
        return hmac.new(self.secret, str(value).encode("utf-8"), hashlib.sha256).hexdigest()[:24]

    @staticmethod
    def _hash(payload):
        return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()

    def verify(self):
        previous = ZERO
        sequence = 0
        if not self.path.exists():
            return sequence, previous
        if self.path.stat().st_mode & 0o077:
            raise PermissionError("Evidence audit file permissions are not private")
        with self.path.open(encoding="utf-8") as log:
            for line_no, line in enumerate(log, 1):
                record = json.loads(line)
                expected_sequence = sequence + 1
                if (record.get("schema") != SCHEMA or
                    record.get("seq") != expected_sequence or
                    record.get("previous_hash") != previous):
                    raise ValueError("Evidence journal sequence broken at line " + str(line_no))
                digest = record.get("hash")
                body = {k:v for k,v in record.items() if k != "hash"}
                if digest != self._hash(body):
                    raise ValueError("Evidence journal hash mismatch at line " + str(line_no))
                previous = digest
                sequence = expected_sequence
        return sequence, previous

    def append(self, stage, **fields):
        if stage not in ALLOWED_STAGES:
            raise ValueError("Unknown evidence journal stage")
        unknown = set(fields) - ALLOWED_FIELDS
        if unknown or (set(fields) & PROHIBITED):
            raise ValueError("Evidence journal has forbidden metadata fields: " + repr(sorted(unknown)))
        if "sources" in fields and not isinstance(fields["sources"], list):
            raise ValueError("sources must be a bounded list of hashed document identifiers")
        if len(fields.get("sources", [])) > 20:
            raise ValueError("Too many source identifiers for metadata journal")
        # Do not silently leak arbitrary nested dictionaries from tools.
        for key, value in fields.items():
            if isinstance(value, dict):
                raise ValueError("Nested audit values are not permitted: " + key)
            if isinstance(value, str) and len(value) > 200:
                raise ValueError("Audit metadata value too long: " + key)
        with self.lock:
            record = {
                "schema": SCHEMA,
                "seq": self.sequence+1,
                "time_utc": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "stage": stage,
                "release": self.release,
                "previous_hash": self.previous,
                **fields,
            }
            digest = self._hash(record)
            record["hash"] = digest
            encoded = _canonical(record) + "\n"
            # append, fsync, and private permissions. Any exception propagates
            # so callers can truthfully record audit failures in service logs.
            fd = os.open(self.path, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
            try:
                os.fchmod(fd, 0o600)
                os.write(fd, encoded.encode("utf-8"))
                os.fsync(fd)
            finally:
                os.close(fd)
            self.sequence += 1
            self.previous = digest
            return record["seq"]

    def safe_append(self, stage, on_error=None, **fields):
        try:
            return self.append(stage, **fields)
        except Exception as exc:
            if on_error:
                on_error("evidence audit failure", type(exc).__name__)
            return None


def verify_journal(path):
    """External integrity check without writing a key or changing the audit."""
    file = Path(path)
    prev = ZERO
    seq = 0
    if not file.exists():
        raise FileNotFoundError(file)
    with file.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            body = {k:v for k,v in row.items() if k != "hash"}
            if (row.get("schema") != SCHEMA or row.get("seq") != seq+1 or
                row.get("previous_hash") != prev or
                row.get("hash") != EvidenceJournal._hash(body)):
                raise ValueError("Audit integrity failure at sequence " + str(seq+1))
            prev = row["hash"]
            seq += 1
    return {"records":seq, "last_hash":prev, "schema":SCHEMA}
