from core.game import available_moves, new_board, get_winner
from core.ai import best_move, make_move
from core.display import display_board, display_help_board

def ask_int(prompt, valid_values=None):
    """Demande un entier valide à l'utilisateur."""
    while True:
        try:
            value = int(input(prompt))
            if valid_values is None or value in valid_values:
                return value
            print(f"  ⚠  Valeur invalide. Choisissez parmi : {valid_values}")
        except ValueError:
            print("  ⚠  Entrez un nombre entier.")


def ask_move(board, player_name):
    """
    Demande au joueur de saisir une ligne et une colonne (1-3).
    Répète jusqu'à obtenir une case libre valide.
    Retourne (row, col) en indices 0-based.
    """
    free = set(available_moves(board))
    while True:
        row = ask_int(f"  {player_name} — Ligne   (1-3) : ", valid_values=[1, 2, 3])
        col = ask_int(f"  {player_name} — Colonne (1-3) : ", valid_values=[1, 2, 3])
        r0, c0 = row - 1, col - 1
        if (r0, c0) not in free:
            print("  ⚠  Cette case est déjà occupée, choisissez-en une autre.\n")
        else:
            return r0, c0


def ask_names(mode):
    """
    Demande les prénoms des joueurs selon le mode.
    Retourne un dict {symbol: nom_affiché}.
    """
    print()
    if mode == "pvp":
        name1 = input("  Nom du Joueur 1 (X) : ").strip() or "Joueur 1"
        name2 = input("  Nom du Joueur 2 (O) : ").strip() or "Joueur 2"
        return {"X": name1, "O": name2}
    else:
        name1 = input("  Votre nom (vous jouez X) : ").strip() or "Joueur"
        return {"X": name1, "O": "Scorpio AI"}

def play_game(mode="pve", difficulty=9):
    """
    Lance une partie complète.

    mode       : "pvp" (deux humains) ou "pve" (humain vs Scorpio AI)
    difficulty : profondeur Minimax, entre 1 (facile) et 9 (impossible)
    """
    names = ask_names(mode)

    board    = new_board()
    players  = ["X", "O"]
    current  = 0            # X commence toujours

    ai_player    = "O"
    human_player = "X"

    print(f"\n  Que la partie commence !")
    print(f"  {names['X']} \033[1;34m(X)\033[0m  vs  {names['O']} \033[1;31m(O)\033[0m\n")
    display_help_board()

    while True:
        player = players[current]
        name   = names[player]

        display_board(board)

        # ── Coup de Scorpio AI ──
        if mode == "pve" and player == ai_player:
            print(f"  {name} réfléchit...\n")
            r, c = best_move(board, ai_player, human_player, depth=difficulty)
            print(f"  {name} joue → Ligne {r + 1}, Colonne {c + 1}\n")

        # ── Coup humain ──
        else:
            r, c = ask_move(board, name)

        # ── Appliquer le coup ──
        board = make_move(board, r, c, player)

        # ── Fin de partie ? ──
        winner = get_winner(board)
        if winner:
            display_board(board)
            if winner == "Draw":
                print("  🤝  Match nul ! Belle partie.\n")
            else:
                print(f"  🏆  {names[winner]} a gagné ! Félicitations !\n")
            break

        current = 1 - current
