from core.game import get_winner, available_moves, make_move

def minimax(board, depth, is_maximizing, ai_player, human_player):
    """
    Minimax récursif.
    - is_maximizing=True  → tour de l'IA    (cherche le MAX)
    - is_maximizing=False → tour du joueur  (cherche le MIN)
    - depth : profondeur restante (= niveau de difficulté)
    """
    winner = get_winner(board)

    if winner == ai_player:        return  1000
    if winner == human_player:     return -1000
    if winner == "Draw" or depth == 0: return 0

    moves = available_moves(board)

    if is_maximizing:
        best = -9999
        for (r, c) in moves:
            score = minimax(make_move(board, r, c, ai_player), depth - 1, False, ai_player, human_player)
            best = max(best, score)
        return best
    else:
        best = 9999
        for (r, c) in moves:
            score = minimax(make_move(board, r, c, human_player), depth - 1, True, ai_player, human_player)
            best = min(best, score)
        return best


def best_move(board, ai_player, human_player, depth=9):
    """Retourne (row, col) du meilleur coup pour Scorpio AI (indices 0-based)."""
    best_score, best_pos = -9999, None
    for (r, c) in available_moves(board):
        score = minimax(make_move(board, r, c, ai_player), depth - 1, False, ai_player, human_player)
        if score > best_score:
            best_score, best_pos = score, (r, c)
    return best_pos
