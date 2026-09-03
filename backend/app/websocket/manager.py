from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.conexoes_ativas: dict[str, WebSocket] = {}

    async def conectar(self, cliente_id: str, websocket: WebSocket):
        await websocket.accept()
        self.conexoes_ativas[cliente_id] = websocket

    def desconectar(self, cliente_id: str):
        if cliente_id in self.conexoes_ativas:
            del self.conexoes_ativas[cliente_id]

    async def enviar_para_cliente(self, cliente_id: str, mensagem: str):
        websocket = self.conexoes_ativas.get(cliente_id)
        if websocket:
            await websocket.send_text(mensagem)

manager = ConnectionManager()