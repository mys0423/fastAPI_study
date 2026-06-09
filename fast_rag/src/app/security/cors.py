from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    """
    CORS 미들웨어 설정
    """
# 허용할 오리진 목록
    origins = [
        "http://localhost:3000", # front
        "http://localhost:7000", # fast rag
        "http://localhost:8000", # fast back
        "http://localhost:10000", # spring
    ]

# CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )