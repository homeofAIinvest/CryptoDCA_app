from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .auth import create_user, authenticate_user, get_current_user
from .sim import run_simulation
import uvicorn

app = FastAPI(title="CryptoDCA.ai API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SignupIn(BaseModel):
    email: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

class SimRequest(BaseModel):
    tickers: list
    monthly: float = 50.0
    start: str = "2019-01-01"
    end: str = None

@app.post('/signup')
def signup(payload: SignupIn):
    ok = create_user(payload.email, payload.password)
    if not ok:
        raise HTTPException(status_code=400, detail='User already exists')
    return {'status':'ok'}

@app.post('/login')
def login(payload: LoginIn):
    token = authenticate_user(payload.email, payload.password)
    if not token:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return {'access_token': token}

@app.post('/simulate')
def simulate(req: SimRequest, user=Depends(get_current_user)):
    out = run_simulation(req.tickers, req.monthly, req.start, req.end)
    return out

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
