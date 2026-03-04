# main.py — WebSocket Edition
"""
Flux PvE  :  POST /games  →  WS /ws/{id}  →  POST /games/{id}/move
Flux PvP  :  POST /games  →  POST /games/{id}/join  →  WS /ws/{id}  →  POST /games/{id}/move
"""

import asyncio
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

from core.game import make_move, get_winner, available_moves
from core.ai   import best_move
from api.game_store import (
    create_game, join_game, get_game,
    find_token_symbol, game_to_dict,
    STATUS_PLAYING, STATUS_FINISHED,
)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ORIGIN   = os.getenv("ORIGIN", "*").split(",")

app = FastAPI(title="Morpion — Scorpio AI", version="2.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=ORIGIN, allow_methods=["*"], allow_headers=["*"]
)


# ── WebSocket Connection Manager ─────────────────────────────

class ConnectionManager:
    """Salles WebSocket : game_id → [WebSocket, ...]"""

    def __init__(self):
        self._rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, game_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._rooms.setdefault(game_id, []).append(ws)

    def disconnect(self, game_id: str, ws: WebSocket) -> None:
        room = self._rooms.get(game_id, [])
        if ws in room:
            room.remove(ws)
        if not room:
            self._rooms.pop(game_id, None)

    async def broadcast(self, game_id: str, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in list(self._rooms.get(game_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(game_id, ws)


manager = ConnectionManager()


# ── Schémas ──────────────────────────────────────────────────

class CreateGameRequest(BaseModel):
    mode:        str = Field(..., description="'pve' ou 'pvp'")
    player_name: str = Field(..., description="Votre prénom")
    difficulty:  int = Field(3,   description="1=Facile 2=Moyen 3=Impossible")

class JoinGameRequest(BaseModel):
    player_name: str

class MoveRequest(BaseModel):
    player_token: str
    row:          int = Field(..., ge=1, le=3)
    col:          int = Field(..., ge=1, le=3)


# ── Helpers ───────────────────────────────────────────────────

async def _run_ai(game) -> None:
    """Minimax dans un thread pour ne pas bloquer l'event loop."""
    row, col = await asyncio.to_thread(
        best_move, game.board, "O", "X", game.difficulty
    )
    game.board = make_move(game.board, row, col, "O")
    winner = get_winner(game.board)
    if winner:
        game.status, game.winner = STATUS_FINISHED, winner
    else:
        game.current_turn = "X"


def _check_end(game) -> None:
    winner = get_winner(game.board)
    if winner:
        game.status, game.winner = STATUS_FINISHED, winner


# ── Routes REST ───────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Morpion Scorpio AI — WebSocket ready"}


@app.post("/games", tags=["Parties"])
def create(req: CreateGameRequest):
    if req.mode not in ("pve", "pvp"):
        raise HTTPException(400, "mode doit être 'pve' ou 'pvp'.")
    if not (1 <= req.difficulty <= 3):
        raise HTTPException(400, "difficulty doit être 1, 2 ou 3.")

    game = create_game(req.mode, req.player_name.strip() or "Joueur", req.difficulty)
    res  = {"player_token": game.players["X"]["token"], "game": game_to_dict(game)}
    if req.mode == "pvp":
        res["invite_url"] = f"{BASE_URL}/games/{game.game_id}/join"
    return res


@app.post("/games/{game_id}/join", tags=["Parties"])
async def join(game_id: str, req: JoinGameRequest):
    try:
        game, token = join_game(game_id, req.player_name.strip() or "Joueur 2")
    except KeyError  as e: raise HTTPException(404, str(e))
    except ValueError as e: raise HTTPException(400, str(e))

    # Notifie le créateur (joueur X) que O a rejoint — instantané !
    await manager.broadcast(game_id, {"type": "state", "game": game_to_dict(game)})
    return {"player_token": token, "game": game_to_dict(game)}


@app.post("/games/{game_id}/move", tags=["Parties"])
async def move(game_id: str, req: MoveRequest):
    try:    game = get_game(game_id)
    except KeyError as e: raise HTTPException(404, str(e))

    if game.status != STATUS_PLAYING:
        raise HTTPException(400, "La partie n'est pas en cours.")

    try:    symbol = find_token_symbol(game, req.player_token)
    except ValueError: raise HTTPException(403, "Token invalide.")

    if symbol != game.current_turn:
        raise HTTPException(400, f"Ce n'est pas votre tour (tour de {game.current_turn}).")

    row0, col0 = req.row - 1, req.col - 1
    if (row0, col0) not in available_moves(game.board):
        raise HTTPException(400, "Cette case est déjà occupée.")

    # Coup du joueur
    game.board = make_move(game.board, row0, col0, symbol)
    _check_end(game)

    if game.mode == "pve" and game.status == STATUS_PLAYING:
        game.current_turn = "O"
        # Broadcast coup humain immédiatement (avant que l'IA calcule)
        await manager.broadcast(game_id, {"type": "state", "game": game_to_dict(game)})
        await _run_ai(game)
    elif game.status == STATUS_PLAYING:
        game.current_turn = "O" if symbol == "X" else "X"

    # Broadcast état final (coup PvP ou résultat après IA)
    await manager.broadcast(game_id, {"type": "state", "game": game_to_dict(game)})
    return {"game": game_to_dict(game)}


@app.get("/games/{game_id}", tags=["Parties"])
def state(game_id: str):
    """Fallback REST si WebSocket indisponible."""
    try:    return {"game": game_to_dict(get_game(game_id))}
    except KeyError as e: raise HTTPException(404, str(e))


@app.get("/games", tags=["Debug"])
def list_games():
    from api.game_store import _games
    return {"count": len(_games), "games": [game_to_dict(g) for g in _games.values()]}


# ── WebSocket ─────────────────────────────────────────────────

@app.websocket("/ws/{game_id}")
async def ws_endpoint(websocket: WebSocket, game_id: str):
    """
    Canal temps réel d'une partie.
    • Connexion  → envoie l'état courant immédiatement.
    • Changement → {"type": "state", "game": {...}} broadcasté à tous les clients.
    • Ping/pong  → le client envoie "ping", le serveur répond "pong".
    • Erreur     → {"type": "error", "detail": "..."} puis fermeture 4004.
    """
    try:
        game = get_game(game_id)
    except KeyError:
        await websocket.accept()
        await websocket.send_json({"type": "error", "detail": f"Partie '{game_id}' introuvable."})
        await websocket.close(code=4004)
        return

    await manager.connect(game_id, websocket)
    try:
        # État initial dès la connexion
        await websocket.send_json({"type": "state", "game": game_to_dict(game)})
        # Keep-alive : écoute les pings
        while True:
            msg = await websocket.receive_text()
            if msg == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(game_id, websocket)
