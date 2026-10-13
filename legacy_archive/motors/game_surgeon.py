import nashpy as nash
import numpy as np


class GameSurgeon:
    def find_manipulation(self, payoff_A, payoff_B):
        A = np.array(payoff_A)
        B = np.array(payoff_B)
        game = nash.Game(A, B)
        equilibria = list(game.support_enumeration())
        return {
            "motor": "Nashpy",
            "equilibrium_found": len(equilibria) > 0,
            "equilibria_count": len(equilibria),
            "negative_finding": "Bu oyunda denge yok, manipülasyon var" if not equilibria else "Oyun dengede"
        }
