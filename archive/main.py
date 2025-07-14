import websocket
import json
import sqlite3
from datetime import datetime
import threading
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn
from fastapi.staticfiles import StaticFiles




# === SQLite Setup ===
conn = sqlite3.connect('hyperliquid_blocks.db', check_same_thread=False)
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS blocks (
        height INTEGER PRIMARY KEY,
        block_time BIGINT,
        block_hash TEXT,
        proposer TEXT,
        num_txs INTEGER
    )
''')
conn.commit()

# === FastAPI Setup ===
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

connected_clients = []

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keeps connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

def broadcast_block(block):
    for client in connected_clients:
        try:
            import asyncio
            asyncio.run(client.send_text(json.dumps(block)))
        except Exception as e:
            print(f"Failed to send block to client: {e}")

# === WebSocket Listener to Hyperliquid ===
def on_message(ws, message):
    try:
        blocks = json.loads(message)

        for block in blocks:
            height = block['height']
            block_time = block['blockTime']  # Keep as raw timestamp
            block_hash = block['hash']
            proposer = block['proposer']
            num_txs = block['numTxs']

            cur.execute('''
                INSERT OR IGNORE INTO blocks (height, block_time, block_hash, proposer, num_txs)
                VALUES (?, ?, ?, ?, ?)
            ''', (height, block_time, block_hash, proposer, num_txs))
            conn.commit()

            print(f"Block {height} saved with {num_txs} transactions.")

            block_data = {
                "height": height,
                "block_time": block_time,
                "block_hash": block_hash,
                "proposer": proposer,
                "num_txs": num_txs
            }
            broadcast_block(block_data)

    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws):
    print("WebSocket closed. Reconnecting in 5 seconds...")
    time.sleep(5)
    start_websocket()

def on_open(ws):
    payload = {
        "method": "subscribe",
        "subscription": {"type": "explorerBlock"}
    }
    ws.send(json.dumps(payload))
    print("WebSocket connection opened and subscribed to explorerBlock.")

def start_websocket():
    ws = websocket.WebSocketApp(
        "wss://rpc.hyperliquid.xyz/ws",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

# === Run WebSocket and FastAPI ===
if __name__ == "__main__":
    listener_thread = threading.Thread(target=start_websocket)
    listener_thread.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)
