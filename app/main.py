from fastapi import FastAPI
from app.routers import trading

app = FastAPI(title="SPIMEX Trading API")

app.include_router(trading.router)


@app.get("/")
def root():
    return {"message": "FastAPI for Effective Mobile"}