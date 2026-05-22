from fastapi import FastAPI
from app.routes import auth, transactions, accounts

app = FastAPI()

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(accounts.router)