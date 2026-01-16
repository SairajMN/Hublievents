"""
Security middleware for Hublievents Backend API.
Provides security headers, CSRF protection, and other security measures.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import secrets
import hashlib
import hmac
import time
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Implements OWASP security headers recommendations.
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",

            # Prevent clickjacking
            "X-Frame-Options": "DENY",

            # XSS protection
            "X-XSS-Protection": "1; mode=block",

            # Referrer policy
            "Referrer-Policy": "strict-origin-when-cross-origin",

            # Content Security Policy (basic)
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # Allow inline scripts for now
                "style-src 'self' 'unsafe-inline'; "  # Allow inline styles
                "img-src 'self' data: https:; "  # Allow images from HTTPS
                "font-src 'self' data:; "  # Allow fonts
                "connect-src 'self'; "  # Allow connections to same origin
                "frame-ancestors 'none';"  # Prevent embedding
            ),

            # HSTS (HTTP Strict Transport Security) - only in production
            # "Strict-Transport-Security": "max-age=31536000; includeSubDomains",

            # Feature policy / Permissions policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), "
                "accelerometer=(), gyroscope=()"
            ),

            # Remove server header for security
            "Server": "Hublievents API",
        }

        # Add headers to response
        for header_name, header_value in headers.items():
            response.headers[header_name] = header_value

        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    Middleware to protect against Cross-Site Request Forgery (CSRF) attacks.
    Uses double-submit cookie pattern with encrypted tokens.
    """

    def __init__(self, app, secret_key: str = None, exempt_paths: list = None):
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_bytes(32)
        self.exempt_paths = exempt_paths or ["/health", "/api/v1/auth/login", "/api/v1/auth/refresh"]

    def _is_exempt_path(self, path: str) -> bool:
        """Check if the path is exempt from CSRF protection."""
        return any(path.startswith(exempt_path) for exempt_path in self.exempt_paths)

    def _generate_csrf_token(self, session_id: str) -> str:
        """Generate a CSRF token based on session ID."""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key,
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        # Return token with timestamp for expiration
        return f"{timestamp}:{signature}"

    def _verify_csrf_token(self, token: str, session_id: str) -> bool:
        """Verify a CSRF token."""
        try:
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)

            # Check if token is not too old (5 minutes)
            if time.time() - timestamp > 300:  # 5 minutes
                return False

            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key,
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)

        except (ValueError, TypeError):
            return False

    def _get_session_id(self, request: Request) -> str:
        """Get or create a session ID from cookies."""
        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = secrets.token_urlsafe(32)
        return session_id

    async def dispatch(self, request: Request, call_next):
        # Skip CSRF protection for exempt paths
        if self._is_exempt_path(request.url.path):
            response = await call_next(request)

            # Set session cookie for exempt paths if not present
            if not request.cookies.get("session_id"):
                session_id = self._get_session_id(request)
                response.set_cookie(
                    key="session_id",
                    value=session_id,
                    httponly=True,
                    secure=True,  # Only send over HTTPS
                    samesite="strict",
                    max_age=86400  # 24 hours
                )

            return response

        # Check if this is a state-changing request
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            session_id = self._get_session_id(request)

            # Get CSRF token from headers
            csrf_token = request.headers.get("X-CSRF-Token")

            # For API requests, also check for token in form data or JSON
            if not csrf_token and request.method == "POST":
                # Check form data
                form_data = await request.form()
                csrf_token = form_data.get("csrf_token")

                # If not in form, check JSON body (without consuming it)
                if not csrf_token:
                    try:
                        body = await request.json()
                        csrf_token = body.get("csrf_token")
                    except:
                        pass

            if not csrf_token:
                logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
                return Response(
                    content='{"error": "CSRF token required"}',
                    status_code=403,
                    media_type="application/json"
                )

            if not self._verify_csrf_token(csrf_token, session_id):
                logger.warning(f"CSRF token verification failed for {request.method} {request.url.path}")
                return Response(
                    content='{"error": "CSRF token invalid or expired"}',
                    status_code=403,
                    media_type="application/json"
                )

        response = await call_next(request)

        # Set CSRF token cookie for GET requests (to be used in subsequent requests)
        if request.method == "GET":
            session_id = self._get_session_id(request)
            csrf_token = self._generate_csrf_token(session_id)

            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=False,  # Allow JavaScript access
                secure=True,     # Only send over HTTPS
                samesite="strict",
                max_age=300      # 5 minutes
            )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log incoming requests for security monitoring.
    """

    async def dispatch(self, request: Request, call_next):
        # Log request details
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        method = request.method
        path = request.url.path

        logger.info(f"Request: {method} {path} from {client_ip} - User-Agent: {user_agent}")

        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            logger.warning(f"Suspicious request detected: {method} {path} from {client_ip}")

        response = await call_next(request)

        # Log response status
        logger.info(f"Response: {response.status_code} for {method} {path}")

        return response

    def _is_suspicious_request(self, request: Request) -> bool:
        """Check for suspicious request patterns."""
        user_agent = request.headers.get("User-Agent", "").lower()

        # Check for common attack patterns
        suspicious_patterns = [
            "../../",  # Path traversal
            "<script",  # XSS attempts
            "union select",  # SQL injection
            "eval(",  # Code injection
            "javascript:",  # JavaScript URL schemes
        ]

        url_path = str(request.url.path).lower()
        query_string = str(request.url.query).lower()

        for pattern in suspicious_patterns:
            if pattern in url_path or pattern in query_string:
                return True

        # Check for empty or suspicious User-Agent
        if not user_agent or user_agent in ["", "-", "null"]:
            return True

        return False


# Rate limiting functionality
def rate_limit(limit: int = 100, window: int = 60):
    """
    Rate limiting dependency for FastAPI routes.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds

    Returns:
        Dependency function that can be used with FastAPI
    """
    def rate_limit_dependency():
        # Simple in-memory rate limiting (use Redis in production)
        # This is a basic implementation - use slowapi or redis for production
        return True  # Placeholder - implement proper rate limiting

    return rate_limit_dependency
