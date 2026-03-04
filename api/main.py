"""
API FastAPI
===================================================
Lancer le serveur :
    pip install fastapi uvicorn
    uvicorn main:app --reload

Documentation interactive : http://localhost:8000/docs

Flux PvE (Joueur vs IA) :
  1. POST /games              → crée la partie, récupère player_token
  2. POST /games/{id}/move    → joue un coup (l'IA répond automatiquement)
  3. GET  /games/{id}         → état courant (polling depuis le frontend)

Flux PvP (via lien d'invitation) :
  1. POST /games              → crée la partie, récupère l'invite_url
  2. Partager l'invite_url au second joueur
  3. POST /games/{id}/join    → le second joueur rejoint, récupère son token
  4. POST /games/{id}/move    → chaque joueur joue à son tour (avec son token)
  5. GET  /games/{id}         → polling pour voir les mises à jour en temps réel
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os

from core.game import make_move, get_winner, available_moves
from core.ai import best_move

from api.game_store import (
    create_game, join_game, get_game,
    find_token_symbol, game_to_dict,
    STATUS_PLAYING, STATUS_FINISHED,
)


# URL de base pour générer les liens d'invitation
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
ORIGIN = os.getenv("ORIGIN", "*").split(',')

app = FastAPI(
    title="Morpion — Scorpio AI",
    description="API pour jouer au morpion contre l'IA ou un ami via lien d'invitation.",
    version="1.0.0",
)

# Autorise toutes les origines (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateGameRequest(BaseModel):
    mode:        str = Field(..., description="'pve' ou 'pvp'")
    player_name: str = Field(..., description="Votre prénom")
    difficulty:  int = Field(3,   description="1=Facile, 2=Moyen, 3=Impossible (PvE uniquement)")


class JoinGameRequest(BaseModel):
    player_name: str = Field(..., description="Votre prénom")


class MoveRequest(BaseModel):
    player_token: str = Field(..., description="Votre token unique reçu à la création/rejoindre")
    row:          int = Field(..., description="Ligne 1-3")
    col:          int = Field(..., description="Colonne 1-3")

def apply_ai_move(game) -> None:
    """
    Calcule et applique le coup de Scorpio AI (joueur O).
    Appelé automatiquement après chaque coup humain en mode PvE.
    Modifie l'objet game en place.
    """
    row, col = best_move(game.board, "O", "X", depth=game.difficulty)
    game.board = make_move(game.board, row, col, "O")

    winner = get_winner(game.board)
    if winner:
        game.status = STATUS_FINISHED
        game.winner = winner
    else:
        game.current_turn = "X"


def check_and_close(game) -> None:
    """Vérifie si la partie est terminée et met à jour le statut."""
    winner = get_winner(game.board)
    if winner:
        game.status = STATUS_FINISHED
        game.winner = winner


@app.get("/", tags=["Info"])
def root():
    """Vérifie que l'API tourne."""
    return {"message": "Morpion - Scorpio AI - API opérationnelle"}


# ── 1. Créer une partie ──────────────────────

@app.post("/games", tags=["Parties"])
def create(req: CreateGameRequest):
    """
    Crée une nouvelle partie.

    **PvE** : la partie commence immédiatement contre Scorpio AI.
    **PvP** : génère un lien d'invitation à partager au second joueur.

    Retourne votre `player_token` (à conserver côté client, ne jamais partager).
    """
    if req.mode not in ("pve", "pvp"):
        raise HTTPException(400, "mode doit être 'pve' ou 'pvp'.")
    if not (1 <= req.difficulty <= 3):
        raise HTTPException(400, "difficulty doit être 1, 2 ou 3.")

    game = create_game(req.mode, req.player_name.strip() or "Joueur", req.difficulty)

    response = {
        "player_token": game.players["X"]["token"],
        "game":         game_to_dict(game),
    }

    # Ajoute le lien d'invitation en PvP
    if req.mode == "pvp":
        response["invite_url"] = f"{BASE_URL}/games/{game.game_id}/join"

    return response


# ── 2. Rejoindre une partie PvP ──────────────

@app.post("/games/{game_id}/join", tags=["Parties"])
def join(game_id: str, req: JoinGameRequest):
    """
    Rejoint une partie PvP via le lien d'invitation.
    Le second joueur reçoit son `player_token` et joue en tant que **O**.
    """
    try:
        game, token = join_game(game_id, req.player_name.strip() or "Joueur 2")
    except KeyError as e:
        raise HTTPException(404, str(e))
    except ValueError as e:
        raise HTTPException(400, str(e))

    return {
        "player_token": token,
        "game":         game_to_dict(game),
    }


# ── 3. Jouer un coup ─────────────────────────

@app.post("/games/{game_id}/move", tags=["Parties"])
def move(game_id: str, req: MoveRequest):
    """
    Joue un coup (ligne + colonne, de 1 à 3).

    - Vérifie que c'est bien votre tour (via `player_token`).
    - En PvE, Scorpio AI joue automatiquement juste après.
    - En PvP, l'adversaire voit le changement via GET `/games/{id}`.
    """
    try:
        game = get_game(game_id)
    except KeyError as e:
        raise HTTPException(404, str(e))

    # Vérifications
    if game.status != STATUS_PLAYING:
        raise HTTPException(400, "La partie n'est pas en cours.")

    try:
        symbol = find_token_symbol(game, req.player_token)
    except ValueError:
        raise HTTPException(403, "Token invalide.")

    if symbol != game.current_turn:
        raise HTTPException(400, f"Ce n'est pas votre tour (tour de {game.current_turn}).")

    if not (1 <= req.row <= 3 and 1 <= req.col <= 3):
        raise HTTPException(400, "Ligne et colonne doivent être entre 1 et 3.")

    row0, col0 = req.row - 1, req.col - 1

    if (row0, col0) not in available_moves(game.board):
        raise HTTPException(400, "Cette case est déjà occupée.")

    # Appliquer le coup du joueur
    game.board = make_move(game.board, row0, col0, symbol)
    check_and_close(game)

    # En PvE et partie toujours en cours → Scorpio AI joue
    if game.mode == "pve" and game.status == STATUS_PLAYING:
        game.current_turn = "O"
        apply_ai_move(game)
    elif game.status == STATUS_PLAYING:
        # PvP : passer au joueur suivant
        game.current_turn = "O" if symbol == "X" else "X"

    return {"game": game_to_dict(game)}


# ── 4. État courant d'une partie ───

@app.get("/games/{game_id}", tags=["Parties"])
def state(game_id: str):
    """
    Retourne l'état courant de la partie.
    Utilisé par le frontend pour le **polling** (appeler toutes les ~1s en PvP).
    """
    try:
        game = get_game(game_id)
    except KeyError as e:
        raise HTTPException(404, str(e))

    return {"game": game_to_dict(game)}


# ── 5. Lister toutes les parties (debug) ─────

@app.get("/games", tags=["Debug"])
def list_games():
    """Liste toutes les parties actives."""
    from api.game_store import _games
    return {
        "count": len(_games),
        "games": [game_to_dict(g) for g in _games.values()],
    }
