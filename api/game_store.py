import uuid
from dataclasses import dataclass, field
from typing import Optional

from core.game import new_board

DIFFICULTY_MAP = {1: 2, 2: 5, 3: 9}   # niveau → profondeur Minimax

STATUS_WAITING  = "waiting"   # PvP : en attente du 2e joueur
STATUS_PLAYING  = "playing"   # partie en cours
STATUS_FINISHED = "finished"  # partie terminée

@dataclass
class Game:
    game_id:      str
    mode:         str            # "pve" ou "pvp"
    difficulty:   int            # profondeur Minimax (2 / 5 / 9)

    # Joueurs : symbol X ou O → {"name": str, "token": str}
    # Le token est un UUID secret qui identifie un joueur (pas d'auth réelle)
    players:      dict = field(default_factory=dict)

    board:        list = field(default_factory=new_board)
    current_turn: str  = "X"          # "X" ou "O"
    status:       str  = STATUS_WAITING
    winner:       Optional[str] = None  # "X", "O", "Draw", ou None

_games: dict[str, Game] = {}


def create_game(mode: str, player_name: str, difficulty: int = 3) -> Game:
    """
    Crée une nouvelle partie et l'enregistre dans le store.
    - En PvE  : les deux joueurs sont créés immédiatement (X = humain, O = IA).
    - En PvP  : seul X est créé ; O rejoindra via /games/{id}/join.
    Retourne l'objet Game créé.
    """
    game_id     = str(uuid.uuid4())[:8]   # court, lisible dans l'URL d'invitation
    depth       = DIFFICULTY_MAP.get(difficulty, 9)
    player_token = str(uuid.uuid4())

    game = Game(
        game_id    = game_id,
        mode       = mode,
        difficulty = depth,
        players    = {"X": {"name": player_name, "token": player_token}},
        status     = STATUS_PLAYING if mode == "pve" else STATUS_WAITING,
    )

    if mode == "pve":
        # L'IA n'a pas besoin de token
        game.players["O"] = {"name": "Scorpio AI", "token": None}

    _games[game_id] = game
    return game


def join_game(game_id: str, player_name: str) -> tuple[Game, str]:
    """
    Un second joueur rejoint une partie PvP en attente.
    Retourne (game, token_joueur_O).
    Lève ValueError si la partie n'existe pas ou n'est pas en attente.
    """
    game = get_game(game_id)

    if game.mode != "pvp":
        raise ValueError("Cette partie n'est pas en mode PvP.")
    if game.status != STATUS_WAITING:
        raise ValueError("Cette partie a déjà commencé ou est terminée.")

    token = str(uuid.uuid4())
    game.players["O"] = {"name": player_name, "token": token}
    game.status = STATUS_PLAYING
    return game, token


def get_game(game_id: str) -> Game:
    """Retourne la partie ou lève KeyError si introuvable."""
    if game_id not in _games:
        raise KeyError(f"Partie '{game_id}' introuvable.")
    return _games[game_id]


def find_token_symbol(game: Game, token: str) -> str:
    """
    Retourne le symbole ('X' ou 'O') associé au token.
    Lève ValueError si le token ne correspond à aucun joueur.
    """
    for symbol, info in game.players.items():
        if info["token"] == token:
            return symbol
    raise ValueError("Token invalide.")


def game_to_dict(game: Game) -> dict:
    """
    Sérialise une Game en dict JSON-friendly pour les réponses API.
    N'expose JAMAIS les tokens dans la réponse publique.
    """
    return {
        "game_id":      game.game_id,
        "mode":         game.mode,
        "difficulty":   game.difficulty,
        "board":        game.board,
        "current_turn": game.current_turn,
        "status":       game.status,
        "winner":       game.winner,
        "players": {
            symbol: {"name": info["name"]}
            for symbol, info in game.players.items()
        },
    }
