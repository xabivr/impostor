# partida.py
# Lógica y datos de la partida con control de eliminaciones y condiciones de victoria

import random
from typing import List, Optional, Dict, Any

DEFAULT_WORDS = ["python", "manzana", "guitarra", "estrella", "avion"]

class Partida:
    """
    Clase que contiene el estado de la partida:
    - num_players: número de jugadores
    - player_names: lista de nombres de jugadores
    - num_impostors: número inicial de impostores
    - impostors: set con índices de impostores vivos
    - word: palabra seleccionada para la partida (los tripulantes la conocen)
    - players: lista de dicts con 'id', 'name', 'role' (estado dinámico) y 'word' (None para impostor)
    - alive: lista booleana por jugador
    - over: boolean indicando si la partida terminó
    - winner: "impostores" | "tripulantes" | None
    """
    def __init__(self,
                 num_players: Optional[int] = None,
                 words: Optional[List[str]] = None,
                 player_names: Optional[List[str]] = None,
                 num_impostors: Optional[int] = None):
        # Determinar número de jugadores y nombres
        if player_names:
            self.num_players = len(player_names)
            self.player_names = [name.strip() or f"Jugador {i}" for i, name in enumerate(player_names)]
        elif num_players:
            if num_players < 3:
                raise ValueError("Se recomienda al menos 3 jugadores.")
            self.num_players = int(num_players)
            self.player_names = [f"Jugador {i}" for i in range(self.num_players)]
        else:
            raise ValueError("Debes especificar num_players o player_names.")

        # Palabras
        self.words = [w.strip() for w in (words or []) if w and w.strip()]
        if not self.words:
            self.words = DEFAULT_WORDS.copy()

        # Número de impostores (por defecto 1)
        if num_impostors is None:
            self.num_impostors = 1
        else:
            self.num_impostors = int(num_impostors)

        # Validación inicial: debe haber al menos 1 impostor y menos impostores que tripulantes
        if self.num_impostors < 1:
            raise ValueError("Debe haber al menos 1 impostor.")
        if self.num_impostors >= (self.num_players - self.num_impostors):
            raise ValueError("El número de impostores no puede ser igual o mayor que el número de tripulantes.")

        # Estado de la partida
        # Elegir impostores aleatoriamente (set de índices vivos)
        self.impostors = set(random.sample(range(self.num_players), k=self.num_impostors))

        # Elegir palabra objetivo
        self.word = random.choice(self.words)

        # Alive flags y construcción de jugadores
        self.alive = [True] * self.num_players
        self.players = []
        for i in range(self.num_players):
            role = "impostor" if i in self.impostors else "tripulante"
            assigned_word = None if role == "impostor" else self.word
            self.players.append({
                "id": i,
                "name": self.player_names[i],
                "role": role,
                "word": assigned_word
            })

        # Fin de juego
        self.over = False
        self.winner: Optional[str] = None  # "impostores" | "tripulantes" | None

    def __init__(self,
                 num_players: Optional[int] = None,
                 words: Optional[List[str]] = None,
                 player_names: Optional[List[str]] = None,
                 num_impostors: Optional[int] = None):
        """
        Inicializa una partida del juego "El Impostor".
        
        Parámetros:
        - num_players: número de jugadores (alternativo a player_names)
        - words: lista de palabras candidatas
        - player_names: lista de nombres de jugadores (alternativo a num_players)
        - num_impostors: número de impostores iniciales
        """
        # Determinar número de jugadores y nombres
        if player_names:
            self.num_players = len(player_names)
            self.player_names = [name.strip() or f"Jugador {i}" for i, name in enumerate(player_names)]
        elif num_players:
            if num_players < 3:
                raise ValueError("Se recomienda al menos 3 jugadores.")
            self.num_players = int(num_players)
            self.player_names = [f"Jugador {i}" for i in range(self.num_players)]
        else:
            raise ValueError("Debes especificar num_players o player_names.")

        # Palabras
        self.words = [w.strip() for w in (words or []) if w and w.strip()]
        if not self.words:
            self.words = DEFAULT_WORDS.copy()

        # Número de impostores (por defecto 1)
        if num_impostors is None:
            self.num_impostors = 1
        else:
            self.num_impostors = int(num_impostors)

        # Validación inicial: debe haber al menos 1 impostor y menos impostores que tripulantes
        if self.num_impostors < 1:
            raise ValueError("Debe haber al menos 1 impostor.")
        if self.num_impostors >= (self.num_players - self.num_impostors):
            raise ValueError("El número de impostores no puede ser igual o mayor que el número de tripulantes.")

        # Estado de la partida
        # Elegir impostores aleatoriamente (set de índices vivos)
        self.impostors = set(random.sample(range(self.num_players), k=self.num_impostors))

        # Elegir palabra objetivo
        self.word = random.choice(self.words)

        # Alive flags y construcción de jugadores
        self.alive = [True] * self.num_players
        self.players = []
        for i in range(self.num_players):
            role = "impostor" if i in self.impostors else "tripulante"
            assigned_word = None if role == "impostor" else self.word
            self.players.append({
                "id": i,
                "name": self.player_names[i],
                "role": role,
                "word": assigned_word
            })

        # Fin de juego
        self.over = False
        self.winner: Optional[str] = None  # "impostores" | "tripulantes" | None

    def summary(self) -> str:
        """Resumen textual (no revela la palabra ni quienes son impostores)."""
        s = f"Partida: {self.num_players} jugadores, {self.num_impostors} impostor(es) inicial(es).\n"
        s += "Jugadores (estado):\n"
        for i, p in enumerate(self.players):
            state = "vivo" if self.alive[i] else "eliminado"
            s += f" - {p['id']}: {p['name']} ({state})\n"
        return s

    def get_player_role(self, player_id: int) -> str:
        """Obtiene el rol del jugador."""
        return self.players[player_id]["role"]

    def get_player_word(self, player_id: int) -> Optional[str]:
        """Obtiene la palabra asignada al jugador (None para impostores)."""
        return self.players[player_id]["word"]

    def guess(self, player_id: int, guess_word: str) -> Dict[str, Any]:
        """
        player_id intenta adivinar la palabra.
        Retorna dict:
        { 'player_id', 'player_name', 'guess', 'correct', 'is_impostor', 'game_over', 'winner' }
        """
        guess_norm = guess_word.strip().lower()
        is_correct = (guess_norm == self.word.lower())
        is_impostor = (self.get_player_role(player_id) == "impostor")
        result = {
            "player_id": player_id,
            "player_name": self.players[player_id]["name"],
            "guess": guess_norm,
            "correct": is_correct,
            "is_impostor": is_impostor,
            "game_over": False,
            "winner": None
        }
        if is_correct:
            # Declarar ganador inmediatamente
            if is_impostor:
                self.over = True
                self.winner = "impostores"
            else:
                self.over = True
                self.winner = "tripulantes"
            result["game_over"] = self.over
            result["winner"] = self.winner
        return result

    def vote(self, votes: Dict[int, int], perform_eject: bool = False) -> Dict[str, Any]:
        """
        votes: dict {voter_id: voted_id}
        Si perform_eject=True, la persona elegida (si la hay) será expulsada (eject).
        Devuelve { 'elected': id_o_None, 'is_impostor': bool, 'counts': {id:count}, 'eject_info': {...} }
        """
        counts: Dict[int, int] = {}
        for v in votes.values():
            counts[v] = counts.get(v, 0) + 1
        if not counts:
            return {"elected": None, "is_impostor": False, "counts": counts, "eject_info": None}

        max_votes = max(counts.values())
        candidates = [pid for pid, c in counts.items() if c == max_votes]
        if len(candidates) > 1:
            # empate
            return {"elected": None, "is_impostor": False, "counts": counts, "eject_info": None}
        elected = candidates[0]
        is_impostor = (elected in self.impostors)
        eject_info = None
        if perform_eject:
            eject_info = self.eject(elected)
        return {"elected": elected, "is_impostor": is_impostor, "counts": counts, "eject_info": eject_info}

    def eject(self, player_id: int) -> Dict[str, Any]:
        """
        Expulsa (elimina) a player_id si está vivo.
        Actualiza sets/flags y comprueba si la partida terminó.
        Retorna info:
        { 'player_id', 'was_alive', 'was_impostor', 'game_over', 'winner', 'reason' }
        """
        info: Dict[str, Any] = {
            "player_id": player_id,
            "was_alive": bool(self.alive[player_id]),
            "was_impostor": player_id in self.impostors,
            "game_over": False,
            "winner": None,
            "reason": ""
        }
        if not self.alive[player_id]:
            info["reason"] = "Jugador ya estaba eliminado."
            return info

        # Marcar eliminado
        self.alive[player_id] = False
        # actualizar rol en players (opcional)
        self.players[player_id]["role"] = "eliminado"

        # Si era impostor, quitarlo del set
        if player_id in self.impostors:
            self.impostors.remove(player_id)
            info["reason"] = "Se expulsó a un impostor."
        else:
            info["reason"] = "Se expulsó a un tripulante."

        # Comprobar condiciones de victoria tras la expulsión
        over_info = self.check_win()
        info["game_over"] = over_info["over"]
        info["winner"] = over_info["winner"]
        if info["game_over"]:
            info["reason"] += " " + over_info["reason"]
        return info

    def check_win(self) -> Dict[str, Any]:
        """
        Comprueba condiciones de victoria y actualiza self.over/self.winner si procede.
        Reglas:
         - Si no quedan impostores vivos -> tripulantes ganan.
         - Si impostores_vivos >= tripulantes_vivos -> impostores ganan.
        Retorna { 'over': bool, 'winner': "impostores"|"tripulantes"|None, 'reason': str }
        """
        if self.over:
            return {"over": True, "winner": self.winner, "reason": "Partida ya finalizada."}

        impostors_vivos = len([i for i in self.impostors if self.alive[i]])
        tripulantes_vivos = len([i for i in range(self.num_players) if self.alive[i] and i not in self.impostors])

        # Si no quedan impostores
        if impostors_vivos == 0:
            self.over = True
            self.winner = "tripulantes"
            reason = "No quedan impostores vivos."
            return {"over": True, "winner": self.winner, "reason": reason}

        # Si impostores >= tripulantes => impostores ganan
        if impostors_vivos >= tripulantes_vivos:
            self.over = True
            self.winner = "impostores"
            reason = f"{impostors_vivos} impostor(es) vs {tripulantes_vivos} tripulante(s) => los impostores controlan la partida."
            return {"over": True, "winner": self.winner, "reason": reason}

        return {"over": False, "winner": None, "reason": "La partida continúa."}

    def is_over(self) -> bool:
        """Devuelve True si la partida ha terminado."""
        return self.over