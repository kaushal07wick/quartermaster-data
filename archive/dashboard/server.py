from fastapi import FastAPI
import sqlite3
from app.config import DB_NAME

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Quartermaster Dashboard Placeholder"}

@app.get("/wallets/")
def get_wallets():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT wallet_address, total_aum FROM wallet_analysis")
    results = cursor.fetchall()
    conn.close()
    return [{"wallet_address": row[0], "total_aum": row[1]} for row in results]
