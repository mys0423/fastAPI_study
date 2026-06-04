from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["sha256-crypt"], deprecated="auto")

# 비밀번호 암호화
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# 비밀번호 검증
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)