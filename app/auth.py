from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.db import SessionLocal, User
from passlib.context import CryptContext


#jwt settings
SECRET_KEY = "guided_energy_4life" #very creative ik
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 #1 hour, bc i don't trust creed

#to extract the token from the header.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def user_exists(username):
    with SessionLocal() as db:
        return db.query(User).filter(User.username == username).first() is not None

def create_user(username, password):
    with SessionLocal() as db:
        user = User(username=username, password=hash_password(password))
        db.add(user)
        db.commit()
        
def authenticate_user(username, password):
    with SessionLocal() as db:
        user = db.query(User).filter(User.username == username).first()
        if user and verify_password(password, user.password):
            return user.username
        return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="nope, bad credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="token's sus")
