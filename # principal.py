# principal.py
# Interfaz y eventos para el juego "El Impostor" (adivinar la palabra)
# Requiere partida.py y graficos.py en la misma carpeta.
# Con fondo de imagen en el lado derecho.

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
from partida import Partida
import graficos
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("El Impostor - Configuración")
        self.partida = None

        # --- Pantalla de configuración ---
        frm = ttk.Frame(root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frm, text="Número de jugadores:").grid(row=0, column=0, sticky="w")
        self.num_players_var = tk.IntVar(value=4)
        self.spin_players = ttk.Spinbox(frm, from_=3, to=12, textvariable=self.num_players_var, width=5)
        self.spin_players.grid(row=0, column=1, sticky="w")

        ttk.Label(frm, text="Nombres de jugadores (una por línea):").grid(row=1, column=0, columnspan=2, sticky="w", pady=(8,0))
        self.txt_names = tk.Text(frm, width=40, height=6)
        self.txt_names.insert("1.0", "Jugador 0\nJugador 1\nJugador 2\nJugador 3")
        self.txt_names.grid(row=2, column=0, columnspan=2, pady=(4,8))

        ttk.Label(frm, text="Número de impostores:").grid(row=3, column=0, sticky="w")
        self.num_impostors_var = tk.IntVar(value=1)
        self.spin_impostors = ttk.Spinbox(frm, from_=1, to=5, textvariable=self.num_impostors_var, width=5)
        self.spin_impostors.grid(row=3, column=1, sticky="w")

        ttk.Label(frm, text="Lista de palabras (una por línea):").grid(row=4, column=0, columnspan=2, sticky="w", pady=(8,0))
        self.txt_words = tk.Text(frm, width=40, height=6)
        self.txt_words.insert("1.0", "manzana\nguitarra\npython\nestrella\navion")
        self.txt_words.grid(row=5, column=0, columnspan=2, pady=(4,8))

        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=6, column=0, columnspan=2, sticky="e")
        ttk.Button(btn_frame, text="Iniciar partida", command=self.iniciar_partida).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Salir", command=root.quit).grid(row=0, column=1, padx=4)

        # Expand
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

    def iniciar_partida(self):
        try:
            n = int(self.num_players_var.get())
        except Exception:
            messagebox.showerror("Error", "Número de jugadores inválido.")
            return

        # Leer nombres: si hay menos nombres que n, completar con Jugador i
        raw_names = [s.strip() for s in self.txt_names.get("1.0", "end").splitlines() if s.strip()]
        if len(raw_names) < n:
            names = raw_names + [f"Jugador {i}" for i in range(len(raw_names), n)]
        else:
            names = raw_names[:n]

        try:
            impostors = int(self.num_impostors_var.get())
        except Exception:
            messagebox.showerror("Error", "Número de impostores inválido.")
            return

        palabras = [w.strip() for w in self.txt_words.get("1.0", "end").splitlines() if w.strip()]
        try:
            # Partida puede lanzar ValueError si impostors >= tripulantes, lo capturamos
            self.partida = Partida(player_names=names, num_impostors=impostors, words=palabras)
        except Exception as e:
            messagebox.showerror("Error creando partida", str(e))
            return

        # Abrir ventana de juego
        self.abrir_ventana_juego()

    def abrir_ventana_juego(self):
        w = tk.Toplevel(self.root)
        w.title("El Impostor - Partida")
        w.geometry("1200x700")
        self.game_window = w

        # --- Contenedor principal: left (avatares) + right (fondo) ---
        main_container = ttk.Frame(w)
        main_container.pack(fill="both", expand=True)

        # --- LADO IZQUIERDO: Controles + Avatares ---
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Barra de controles (botones)
        topfrm = ttk.Frame(left_panel)
        topfrm.pack(fill="x", pady=(0, 10))

        ttk.Label(topfrm, text=f"Jugadores: {self.partida.num_players}").pack(side="left")
        ttk.Button(topfrm, text="Mostrar mi rol", command=self.mostrar_rol).pack(side="right", padx=4)
        ttk.Button(topfrm, text="Votar", command=self.iniciar_votacion).pack(side="right", padx=4)
        ttk.Button(topfrm, text="Adivinar palabra", command=self.adivinar_palabra).pack(side="right", padx=4)
        ttk.Button(topfrm, text="Terminar partida", command=lambda: self.terminar_partida(w)).pack(side="right", padx=4)

        # Contenedor de avatares (grid)
        self.canvas_frame = ttk.Frame(left_panel)
        self.canvas_frame.pack(fill="both", expand=True)

        # Mostrar avatares en una grilla
        cols = 2  # reducir a 2 columnas para que quepan mejor en el lado izquierdo
        size = 100
        self.avatar_cards = []  # guardar referencias para actualizar después
        for i in range(self.partida.num_players):
            r = i // cols
            c = i % cols
            card = ttk.Frame(self.canvas_frame, relief="ridge", padding=6)
            card.grid(row=r, column=c, padx=6, pady=6, sticky="n")
            self.avatar_cards.append(card)

            # Crear Canvas para dibujar avatar usando graficos.draw_avatar
            c_canvas = tk.Canvas(card, width=size, height=size, bg="white", highlightthickness=0)
            c_canvas.pack()
            # Usamos como seed el id para que sea determinista
            graficos.draw_avatar(c_canvas, size/2, size/2, size, seed=i)
            
            # Nombre del jugador
            name_label = ttk.Label(card, text=f"{self.partida.players[i]['name']}")
            name_label.pack(pady=(6,0))
            name_label.tag = name_label
            
            # Estado (vivo/eliminado)
            state_label = ttk.Label(card, text="Vivo", foreground="green")
            state_label.pack(pady=2)
            state_label.player_id = i
            state_label.tag = state_label
            
            ttk.Button(card, text="Ver rol (privado)", command=lambda pid=i: self.mostrar_rol_privado(pid)).pack(pady=4)

        # Ajustes de grid
        for col in range(cols):
            self.canvas_frame.grid_columnconfigure(col, weight=1)

        # --- LADO DERECHO: Fondo de imagen ---
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Canvas con fondo
        self.bg_canvas = tk.Canvas(right_panel, bg="white", highlightthickness=0)
        self.bg_canvas.pack(fill="both", expand=True)

        # Cargar y dibujar fondo (buscar imagen en assets/)
        # Soporta varias extensiones y nombres
        bg_paths = [
            "assets/background.png",
            "assets/background.jpg",
            "background.png",
            "background.jpg",
        ]
        bg_found = None
        for path in bg_paths:
            if os.path.exists(path):
                bg_found = path
                break

        if bg_found:
            graficos.set_background(bg_found)
            # Dibujar fondo tras esperar a que el canvas tenga tamaño
            w.after(200, self._draw_bg_on_resize)
        else:
            # Si no encuentra imagen, mostrar degradado simple (opcional)
            self.bg_canvas.create_rectangle(0, 0, 500, 500, fill="#FF6B9D", outline="#FF6B9D")

        # Bind para redibujar fondo si la ventana se redimensiona
        self.bg_canvas.bind("<Configure>", self._on_canvas_resize)

    def _draw_bg_on_resize(self, event=None):
        """Redibujar el fondo cuando cambia el tamaño del canvas."""
        w = self.bg_canvas.winfo_width()
        h = self.bg_canvas.winfo_height()
        if w > 1 and h > 1:
            graficos.draw_background(self.bg_canvas, width=w, height=h, tag="bg")

    def _on_canvas_resize(self, event):
        """Callback cuando el canvas se redimensiona."""
        self._draw_bg_on_resize()

    def mostrar_rol(self):
        if not self.partida:
            return
        pid = simpledialog.askinteger("Mostrar rol", f"Introduce tu número de jugador (0..{self.partida.num_players-1}):", parent=self.game_window, minvalue=0, maxvalue=self.partida.num_players-1)
        if pid is None:
            return
        if not self.partida.alive[pid]:
            messagebox.showinfo("Tu rol", "Estás eliminado.", parent=self.game_window)
            return
        role = self.partida.get_player_role(pid)
        if role == "impostor":
            msg = f"Eres el IMPOSTOR. No tienes palabra asignada."
        else:
            word = self.partida.get_player_word(pid)
            msg = f"Eres un tripulante. Tu palabra es: {word}"
        messagebox.showinfo("Tu rol", msg, parent=self.game_window)

    def mostrar_rol_privado(self, pid):
        if not self.partida:
            return
        if not self.partida.alive[pid]:
            messagebox.showinfo("Rol", f"{self.partida.players[pid]['name']}: estás eliminado.", parent=self.game_window)
            return
        role = self.partida.get_player_role(pid)
        if role == "impostor":
            msg = f"{self.partida.players[pid]['name']} (Jugador {pid}): ERES EL IMPOSTOR.\n(No tienes palabra)."
        else:
            word = self.partida.get_player_word(pid)
            msg = f"{self.partida.players[pid]['name']} (Jugador {pid}): Tripulante.\nTu palabra: {word}"
        t = tk.Toplevel(self.game_window)
        t.title(f"Jugador {pid} - Rol")
        ttk.Label(t, text=msg, padding=12).pack()
        ttk.Button(t, text="Cerrar", command=t.destroy).pack(pady=8)

    def iniciar_votacion(self):
        if not self.partida or self.partida.is_over():
            messagebox.showinfo("Votación", "No hay partida activa o la partida ya terminó.", parent=self.game_window)
            return

        votes = {}
        for voter in range(self.partida.num_players):
            if not self.partida.alive[voter]:
                continue
            prompt = f"{self.partida.players[voter]['name']} (Jugador {voter}), ¿a quién votas? (0..{self.partida.num_players-1})\nSi quieres abstenerte, pulsa Cancelar."
            voted = simpledialog.askinteger("Votación", prompt, parent=self.game_window, minvalue=0, maxvalue=self.partida.num_players-1)
            if voted is None:
                continue
            votes[voter] = voted

        resultado = self.partida.vote(votes, perform_eject=True)
        counts = resultado["counts"]
        elected = resultado["elected"]
        eject_info = resultado.get("eject_info")

        texto = "Resultados de la votación:\n"
        if not counts:
            texto += "No se emitieron votos.\n"
        else:
            for pid in range(self.partida.num_players):
                texto += f"Jugador {pid} ({self.partida.players[pid]['name']}): {counts.get(pid,0)}\n"

        if elected is None:
            texto += "\nNo hay un elegido (empate o nadie)."
            messagebox.showinfo("Votación", texto, parent=self.game_window)
            return

        # Mostrar info de expulsión
        if eject_info:
            texto += f"\nElegido: Jugador {elected} ({self.partida.players[elected]['name']}).\n"
            texto += eject_info["reason"] + "\n"
            if eject_info["was_impostor"]:
                texto += "Se expulsó a un impostor.\n"
            else:
                texto += "Se expulsó a un tripulante.\n"

            if eject_info["game_over"]:
                if eject_info["winner"] == "impostores":
                    texto += "\n¡Los IMPOSTORES han ganado!\n"
                elif eject_info["winner"] == "tripulantes":
                    texto += "\n¡Los TRIPULANTES han ganado!\n"

            # Actualizar estado visual del jugador eliminado
            self.actualizar_estado_jugador(elected)

        messagebox.showinfo("Votación", texto, parent=self.game_window)

        # Si la partida terminó, deshabilitar botones
        if self.partida.is_over():
            self.mostrar_fin_partida()

    def actualizar_estado_jugador(self, player_id: int):
        """Actualiza la etiqueta de estado (vivo/eliminado) del jugador en la UI."""
        if player_id < len(self.avatar_cards):
            card = self.avatar_cards[player_id]
            # Buscar la etiqueta de estado dentro del card (la segunda Label)
            labels = [w for w in card.winfo_children() if isinstance(w, ttk.Label)]
            if len(labels) >= 2:
                state_label = labels[1]
                state_label.config(text="Eliminado", foreground="red")

    def adivinar_palabra(self):
        if not self.partida or self.partida.is_over():
            messagebox.showinfo("Adivinar", "No hay partida activa o ya terminó.", parent=self.game_window)
            return
        pid = simpledialog.askinteger("Adivinar palabra", f"Introduce tu número de jugador (0..{self.partida.num_players-1}):", parent=self.game_window, minvalue=0, maxvalue=self.partida.num_players-1)
        if pid is None:
            return
        if not self.partida.alive[pid]:
            messagebox.showinfo("Adivinar", "Estás eliminado y no puedes adivinar.", parent=self.game_window)
            return
        guess = simpledialog.askstring("Adivinar palabra", "Introduce la palabra que crees que es:", parent=self.game_window)
        if not guess:
            return
        resultado = self.partida.guess(pid, guess)
        if resultado["correct"]:
            if resultado["is_impostor"]:
                messagebox.showinfo("Adivinanza", f"El impostor (Jugador {pid}) adivinó correctamente. ¡Impostores ganan!", parent=self.game_window)
            else:
                messagebox.showinfo("Adivinanza", f"Jugador {pid} adivinó correctamente. ¡Tripulantes ganan!", parent=self.game_window)
            # marcar fin de partida (ya lo hace Partida.guess)
            if self.partida.is_over():
                self.mostrar_fin_partida()
        else:
            messagebox.showinfo("Adivinanza", f"No es correcto. La palabra no es '{resultado['guess']}'.", parent=self.game_window)

    def mostrar_fin_partida(self):
        if not self.partida:
            return
        if not self.partida.is_over():
            return
        if self.partida.winner == "impostores":
            messagebox.showinfo("Fin de partida", "¡Los IMPOSTORES han ganado la partida!", parent=self.game_window)
        elif self.partida.winner == "tripulantes":
            messagebox.showinfo("Fin de partida", "¡Los TRIPULANTES han ganado la partida!", parent=self.game_window)

    def terminar_partida(self, window):
        if messagebox.askyesno("Terminar", "¿Deseas terminar la partida actual?", parent=window):
            window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()