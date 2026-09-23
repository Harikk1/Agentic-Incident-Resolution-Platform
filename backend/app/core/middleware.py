import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or f"req-{uuid.uuid4().hex[:8]}"
        incident_id = request.headers.get("X-Incident-ID")
        session_id = request.headers.get("X-Session-ID") or f"ses-{uuid.uuid4().hex[:8]}"

        # Store in request state
        request.state.request_id = request_id
        request.state.incident_id = incident_id
        request.state.session_id = session_id

        start_time = time.time()
        response: Response = await call_next(request)
        duration = time.time() - start_time

        # Set correlation headers
        response.headers["X-Request-ID"] = request_id
        if incident_id:
            response.headers["X-Incident-ID"] = incident_id
        response.headers["X-Session-ID"] = session_id
        response.headers["X-Response-Time"] = f"{duration*1000:.2f}ms"

        return response
