from datetime import UTC, datetime, timedelta

import jwt
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from app.config import settings


password_hash = PasswordHash.recommended()

# This URL needs to match the login endpoint path. It extracts the token from the authorization bearer when the client
# send it. This enables the "authorize" button in the API docs, making testing much easier.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "api/users/token")


def hash_password(password: str) -> str:
    return password_hash.hash(password = password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Returns true if the hash of the plain password and the hashed password match.
    return password_hash.verify(password = plain_password, hash = hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    
    to_encode: dict = data.copy()
    
    if expires_delta:
        expire: datetime = datetime.now(tz = UTC) + expires_delta
    else:
        expire = datetime.now(tz = UTC) + timedelta(
            minutes = settings.access_token_expire_minutes,
        )
    
    to_encode.update({"exp": expire})
    encoded_jwt: str = jwt.encode(
        payload = to_encode,
        key = settings.secret_key.get_secret_value(),
        algorithm = settings.algorithm,
    )
    
    return encoded_jwt


def verify_access_token(token: str) -> str | None:
    """Verify a JWT access token and return the subject (user ID) if valid."""
    
    try:
        payload: dict = jwt.decode(
            jwt = token,
            key = settings.secret_key.get_secret_value(),
            algorithms = [settings.algorithm],
            options = {
                "require": ["exp", "sub"],
            },
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get("sub")
