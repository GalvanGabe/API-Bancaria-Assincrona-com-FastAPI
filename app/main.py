from fastapi import FastAPI
from app.routes import auth, transactions

app = FastAPI()

app.include_router(auth.router)
app.include_router(transactions.router)