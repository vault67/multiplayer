from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.clients: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.clients:
            self.clients.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.clients:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return FileResponse("./index.html")


@app.websocket("/ws/{client}")
async def websocket_endpoint(websocket: WebSocket, client: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # await manager.send_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client} left the chat")


if __name__ == '__main__':
    uvicorn.run(app, host="p1")
