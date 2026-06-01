from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

"""
보안 관련 HTTP 헤더를 추가하는 미들웨어
"""
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

# 클릭재킹 방지
        response.headers["X-Frame-Options"] = "DENY"

# MIME 타입 스니핑 방지
        response.headers["X-Content-Type-Options"] = "nosniff"

# XSS 방지(CSP)
# 기본적으로 같은 출처에서만 리소스 로드 허용
# "script-src 'self' 'unsafe-inline' https:;"
# 스크립트는 같은 출처와 인라인 스크립트 허용"style-src 'self' 'unsafe-inline' https:;"
# 스타일은 같은 출처와 인라인 스타일 허용"img-src 'self' data: https:;"
# 이미지는 같은 출처와 data URI 허용"font-src 'self' https:;"
# 폰트는 같은 출처에서만 허용"connect-src 'self' https:;"# AJAX, WebSocket 등의 연결은 같은 출처에서만 허용 "frame-ancestors 'none';"
# 프레임에 페이지 포함 금지 (X-Frame-Options 강화)"form-action 'self';"
# 폼 제출은 같은 출처로만 허용"block-all-mixed-content;
# 혼합 콘텐츠(HTTPS 페이지에서 HTTP 리소스) 차단

        response.headers["Content-Security-Policy"] = (
            "default-src 'self' 'unsafe-inline' https:;"
        )

        return response

"""
보안 미들웨어 설정
"""
def setup_security(app: FastAPI):
    app.add_middleware(SecurityHeadersMiddleware)