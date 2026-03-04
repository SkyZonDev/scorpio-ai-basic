


COLOR = {
    "X": "\033[1;34mX\033[0m",
    "O": "\033[1;31mO\033[0m",
    " ": " ",
}

def display_board(board):
    """Affiche le plateau avec bordures, numéros de lignes et colonnes."""
    print()
    print("           Col 1   Col 2   Col 3")
    print("        ┌───────┬───────┬───────┐")
    for row in range(3):
        cells = [COLOR[board[row][col]] for col in range(3)]
        print(f"  Lig {row + 1} │   {cells[0]}   │   {cells[1]}   │   {cells[2]}   │")
        if row < 2:
            print("        ├───────┼───────┼───────┤")
    print("        └───────┴───────┴───────┘")
    print()


def display_help_board():
    """Affiche un plateau exemple pour expliquer la saisie."""
    print("  Comment jouer ? Entrez la ligne puis la colonne (de 1 à 3).\n")
    print("        Col 1   Col 2   Col 3")
    print("        ┌───────┬───────┬───────┐")
    for row in range(1, 4):
        print(f"  Lig {row} │ L{row} C1 │ L{row} C2 │ L{row} C3 │")
        if row < 3:
            print("        ├───────┼───────┼───────┤")
    print("        └───────┴───────┴───────┘")
    print()

