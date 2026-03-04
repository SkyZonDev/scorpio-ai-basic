"""
Morpion (Tic-Tac-Toe) - CLI
"""
from core.cli import ask_int, play_game

BANNER = """
  ╔══════════════════════════════════════╗
  ║        MORPION  —  Scorpio AI        ║
  ╚══════════════════════════════════════╝
"""

def main():
    print(BANNER)
    print("  1 — Joueur vs Joueur      (PvP)")
    print("  2 — Joueur vs Scorpio AI  (PvE)")
    print()

    mode_choice = ask_int("  Votre choix : ", valid_values=[1, 2])
    mode = "pvp" if mode_choice == 1 else "pve"

    difficulty = 9
    if mode == "pve":
        print()
        print("  Niveau de difficulté :")
        print("  1 — Facile     (Scorpio AI regarde 2 coups à l'avance)")
        print("  2 — Moyen      (Scorpio AI regarde 5 coups à l'avance)")
        print("  3 — Impossible (Scorpio AI calcule la partie entière)")
        print()
        level = ask_int("  Votre choix : ", valid_values=[1, 2, 3])
        difficulty = {1: 2, 2: 5, 3: 9}[level]

    play_game(mode=mode, difficulty=difficulty)

    again = input("  Rejouer ? (o/n) : ").strip().lower()
    if again == "o":
        main()
    else:
        print("\n  À bientôt !\n")


if __name__ == "__main__":
    main()
