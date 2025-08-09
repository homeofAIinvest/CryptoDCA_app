import sqlite3, os
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

PWD_CTX = CryptContext(schemes=["bcrypt"], deprecated="auto")
DB = 'users.db'
SECRET = os.environ.get('JWT_SECRET', 'change_this_secret_in_prod')

if not os.path.exists(DB):
    conn = sqlite3.connect(DB)
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)')
    conn.commit()
    conn.close()

def create_user(email, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (email,password) VALUES (?,?)', (email, PWD_CTX.hash(password)))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def authenticate_user(email, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT password FROM users WHERE email=?', (email,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    hashed = row[0]
    if not PWD_CTX.verify(password, hashed):
        return None
    payload = {'sub': email, 'exp': datetime.utcnow() + timedelta(hours=8)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token

bearer = HTTPBearer()

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer)):
    token = creds.credentials
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        return data['sub']
    except Exception:
        raise HTTPException(status_code=401, detail='Invalid token')
