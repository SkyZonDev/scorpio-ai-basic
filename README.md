# Morpion (Tic-Tac-Toe) — Scorpio AI (BASIC)

Petit jeu de morpion jouable dans le terminal, avec deux modes :

* **Joueur vs Joueur (PvP)**
* **Joueur vs IA (PvE)** avec une IA nommée **Scorpio**, basée sur l’algorithme **Minimax**.

⚠️ Cette version est une **édition BASIC de démonstration**.
👉 La version officielle avancée de **Scorpio AI** est disponible ici :
🔗 [https://github.com/SkyZonDev/scorpio-ai-official](https://github.com/SkyZonDev/scorpio-ai-official)

---

## 🚀 Prérequis

* **Python 3.8+** (recommandé)
* Aucun package externe : le projet n’utilise que la bibliothèque standard.

Pour vérifier votre version de Python :

```bash
python --version
# ou
python3 --version
```

---

## 📁 Structure du projet

* `main.py`
  Point d’entrée de l’application (menu principal, choix du mode et de la difficulté).

* `core/cli.py`
  Logique d’interaction en ligne de commande (saisie des coups, boucle de jeu).

* `core/display.py`
  Affichage du plateau et d’un plateau d’aide (numéros de lignes/colonnes).

* `core/game.py`
  Logique du jeu (plateau, coups possibles, détection du gagnant, égalité…).

* `core/ai.py`
  Implémentation de l’IA **Scorpio** avec l’algorithme Minimax et choix du meilleur coup.

---

## ▶️ Lancer le jeu

Depuis la racine du projet (là où se trouve `main.py`) :

```bash
python main.py
# ou selon votre configuration
python3 main.py
```

Un écran d’accueil s’affiche, puis vous pouvez choisir :

* **1 — Joueur vs Joueur (PvP)**
* **2 — Joueur vs Scorpio AI (PvE)**

---

## 🎮 Règles et commandes

Le morpion se joue sur un plateau **3x3** :

* Le joueur **X** commence toujours.
* On gagne en alignant **3 symboles identiques** (X ou O) en ligne, colonne ou diagonale.
* S’il n’y a plus de cases libres et aucun gagnant, la partie est **nulle**.

Dans le terminal, pour jouer un coup :

1. Saisir la **ligne** (1 à 3)
2. Saisir la **colonne** (1 à 3)

Un plateau d’aide (`L1 C1`, `L1 C2`, etc.) s’affiche pour indiquer les positions possibles.

---

## 🤖 Mode Joueur vs Scorpio AI (PvE)

En mode PvE, vous jouez **X** et l’IA **Scorpio** joue **O**.

Vous pouvez choisir un niveau de difficulté, qui correspond à la **profondeur de recherche** de l’algorithme Minimax :

1. **Facile** : l’IA regarde **2 coups** à l’avance
2. **Moyen** : l’IA regarde **5 coups** à l’avance
3. **Impossible** : l’IA calcule la **partie complète** (profondeur max = 9)

Plus la profondeur est grande, plus l’IA :

* est **forte** (difficile à battre),
* mais peut être un peu plus **lente** à jouer sur certaines machines.

---

## 🔧 Détails techniques (aperçu)

* Le plateau est un tableau 3x3 de chaînes `" "`, `"X"`, `"O"`.
* Les fonctions principales :

  * `new_board()` : crée un plateau vide
  * `available_moves(board)` : liste les coups possibles
  * `get_winner(board)` : détecte un gagnant ou un match nul
  * `make_move(board, row, col, player)` : applique un coup (plateau immuable)
  * `minimax(...)` et `best_move(...)` : cœur de l’IA Scorpio

---

## 🌌 Version officielle — Scorpio AI

Cette version est une **implémentation simplifiée à but pédagogique**.

La version officielle de **Scorpio AI** inclut :

* 🔥 Optimisations avancées (Alpha-Beta Pruning)
* 🧠 Systèmes d’évaluation dynamiques
* 🎯 IA adaptative
* 📊 Statistiques de parties
* 🌐 Interface graphique (selon version)
* 🚀 Performances améliorées

👉 Accéder à la version complète :
🔗 [https://github.com/SkyZonDev/scorpio-ai-official](https://github.com/SkyZonDev/scorpio-ai-official)

---

## ✅ Lancer une nouvelle partie

À la fin d’une partie, le programme vous propose :

```text
Rejouer ? (o/n) :
```

* Tapez `o` pour enchaîner une nouvelle partie.
* Tapez `n` (ou autre) pour quitter.

---

# 📜 Licence — MIT

Ce projet est sous licence **MIT**.
