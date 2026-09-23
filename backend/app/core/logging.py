import json
import logging
import time
import os
from typing import Optional, Dict, Any
from backend.app.core.config import settings

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": getattr(record, "timestamp", time.time()),
            "iso_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(getattr(record, "timestamp", time.time()))),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": getattr(record, "service", "smartops-backend"),
            "request_id": getattr(record, "request_id", None),
            "incident_id": getattr(record, "incident_id", None),
            "session_id": getattr(record, "session_id", None),
            "tool": getattr(record, "tool", None),
        }
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            # Sanitize secrets
            sanitized = {k: ("[REDACTED]" if "secret" in k.lower() or "key" in k.lower() or "token" in k.lower() else v) 
                         for k, v in record.extra_fields.items()}
            log_obj["data"] = sanitized
        return json.dumps(log_obj)

# Local In-Memory Buffer for Logs when Elasticsearch is mock or offline
LOG_BUFFER = []

class SmartOpsLogger:
    def __init__(self, name: str = "smartops"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)

    def log(
        self,
        level: str,
        message: str,
        service: str = "smartops-backend",
        request_id: Optional[str] = None,
        incident_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tool: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        log_entry = {
            "timestamp": time.time(),
            "level": level.upper(),
            "message": message,
            "service": service,
            "request_id": request_id,
            "incident_id": incident_id,
            "session_id": session_id,
            "tool": tool,
            "data": extra or {}
        }
        
        # Buffer locally
        LOG_BUFFER.append(log_entry)
        if len(LOG_BUFFER) > 2000:
            LOG_BUFFER.pop(0)

        # Log through Python logging
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        extra_dict = {
            "service": service,
            "request_id": request_id,
            "incident_id": incident_id,
            "session_id": session_id,
            "tool": tool,
            "extra_fields": extra or {}
        }
        log_method(message, extra=extra_dict)

    def info(self, msg: str, **kwargs):
        self.log("info", msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self.log("warning", msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self.log("error", msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self.log("critical", msg, **kwargs)

    def debug(self, msg: str, **kwargs):
        self.log("debug", msg, **kwargs)

    def search_logs(self, service: Optional[str] = None, severity: Optional[str] = None, query: Optional[str] = None, limit: int = 50):
        results = []
        for entry in reversed(LOG_BUFFER):
            if service and entry.get("service") != service:
                continue
            if severity and entry.get("level") != severity.upper():
                continue
            if query and query.lower() not in entry.get("message", "").lower():
                continue
            results.append(entry)
            if len(results) >= limit:
                break
        return results

logger = SmartOpsLogger("smartops")
