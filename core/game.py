def new_board():
    """Retourne un plateau vide 3x3 (liste de listes)."""
    return [[" " for _ in range(3)] for _ in range(3)]


def get_winner(board):
    """
    Retourne 'X', 'O' si l'un d'eux a gagné, 'Draw' en cas d'égalité,
    ou None si la partie est en cours.
    """
    # Lignes
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != " ":
            return board[r][0]

    # Colonnes
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != " ":
            return board[0][c]

    # Diagonales
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]

    # Égalité si aucune case vide
    if all(cell != " " for row in board for cell in row):
        return "Draw"

    return None


def available_moves(board):
    """Retourne la liste des cases vides sous forme de couples (row, col) 0-based."""
    return [(r, c) for r in range(3) for c in range(3) if board[r][c] == " "]


def make_move(board, row, col, player):
    """
    Joue un coup : retourne un NOUVEAU plateau (non destructif).
    Lève ValueError si la case est déjà prise.
    """
    if board[row][col] != " ":
        raise ValueError("Case déjà occupée.")
    new = [line[:] for line in board]
    new[row][col] = player
    return new
