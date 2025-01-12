from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from database import db
from uuid import uuid4
from starlette.requests import Request

# JWT 토큰 설정
# openssl rand -hex 32로 생성, 프로덕션 환경으로 이동하기 전에 secret_key 바꿀 예정, 그땐 git에 업로드 x
SECRET_KEY = "cc9de4a7ed495f04babbfe43da3cab6882b591db39a2a8689eaedff58a623031"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/login")
admin_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/accounts/admin/login")


# 세션에서 토큰을 가져오는 함수 추가
async def get_token_from_session(request: Request):
    return request.session.get('token')


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": str(uuid4())})  # JTI added
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_accounts(email: str, password: str, is_admin):
    if is_admin is False:
        account = await db["users"].find_one({"useremail": email})
    else:
        account = await db["admins"].find_one({"adminemail": email})
    if account and verify_password(password, account.get('userpassword' if not is_admin else 'adminpassword')):
        return account
    return None


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        if payload.get("jti") is None or await is_token_blacklisted(db, payload["jti"]):
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await db["users"].find_one({"useremail": email})
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin(token: str = Depends(admin_oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = decode_access_token(token)
        if payload.get("jti") is None or await is_token_blacklisted(db, payload["jti"]):
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = await db["admins"].find_one({"adminemail": email})
    if admin is None:
        raise credentials_exception
    return admin


async def is_token_blacklisted(db, token_jti: str):
    blacklisted_token = await db["token_blacklist"].find_one({"jti": token_jti})
    return blacklisted_token is not None
