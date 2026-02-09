# graficos.py
# Clase Graficos con __init__ y soporte para imagen de fondo (Pillow recomendado)

import random
from typing import List, Optional

try:
    from PIL import Image, ImageTk
    _HAS_PIL = True
except Exception:
    Image = None
    ImageTk = None
    _HAS_PIL = False

DEFAULT_COLORS = [
    "#e57373", "#64b5f6", "#81c784", "#ffd54f", "#ba68c8", "#4db6ac", "#ff8a65"
]

class Graficos:
    """
    Clase que gestiona configuración de dibujo de avatares y fondo.
    
    Atributos:
    - colors: lista de colores a escoger para avatares
    - bg: color de fondo por defecto para canvas
    - default_with_border: si los avatares dibujan borde por defecto
    - background_path: ruta al archivo de imagen que se usará como fondo (opcional)
    
    Métodos principales:
    - draw_avatar: dibuja un avatar individual en un canvas
    - make_avatar_canvas: crea un canvas con un avatar
    - set_background: carga una imagen de fondo
    - draw_background: dibuja la imagen en un canvas escalada
    - clear_background: elimina la imagen de fondo cargada
    """
    def __init__(self,
                 colors: Optional[List[str]] = None,
                 bg: str = "white",
                 default_with_border: bool = True,
                 background_path: Optional[str] = None):
        """
        Inicializa la clase Graficos.
        
        Parámetros:
        - colors: lista de colores hexadecimales para avatares. Si es None usa DEFAULT_COLORS.
        - bg: color de fondo para canvas (si no hay imagen de fondo).
        - default_with_border: si los avatares deben tener borde por defecto.
        - background_path: ruta a la imagen de fondo (opcional).
        """
        self.colors = colors.copy() if colors else DEFAULT_COLORS.copy()
        self.bg = bg
        self.default_with_border = default_with_border

        # Background image attributes
        self.background_path: Optional[str] = None
        self._bg_pil = None   # PIL.Image (original)
        self._bg_tk = None    # ImageTk.PhotoImage (resized and displayed)
        if background_path:
            self.set_background(background_path)

    # ================ Background methods ================
    def set_background(self, path: str) -> bool:
        """
        Carga la imagen de fondo desde `path`. Requiere Pillow (PIL).
        
        Parámetros:
        - path: ruta a la imagen (soporta .png, .jpg, etc.)
        
        Devuelve:
        - True si se cargó correctamente, False en caso contrario.
        """
        self.background_path = path
        self._bg_pil = None
        self._bg_tk = None
        if not _HAS_PIL:
            return False
        try:
            img = Image.open(path).convert("RGBA")
            self._bg_pil = img
            return True
        except Exception:
            self._bg_pil = None
            return False

    def clear_background(self):
        """Elimina la imagen de fondo cargada."""
        self.background_path = None
        self._bg_pil = None
        self._bg_tk = None

    def draw_background(self, canvas, width: Optional[int] = None, height: Optional[int] = None, tag: str = "bg") -> bool:
        """
        Dibuja la imagen de fondo en el canvas escalada para cubrir el área (cover mode).
        
        Parámetros:
        - canvas: tkinter.Canvas donde dibujar.
        - width/height: tamaño destino. Si es None intenta usar canvas.winfo_width/height().
        - tag: etiqueta para el objeto en el canvas (para manipularlo después).
        
        Devuelve:
        - True si dibujó correctamente, False en caso contrario.
        """
        # Sin PIL o sin imagen cargada
        if not _HAS_PIL or self._bg_pil is None:
            return False

        # Determinar tamaño
        try:
            if width is None:
                width = int(canvas.winfo_width())
            if height is None:
                height = int(canvas.winfo_height())
        except Exception:
            # fallback a atributos del widget
            try:
                width = width or int(canvas['width'])
                height = height or int(canvas['height'])
            except Exception:
                return False

        if width <= 0 or height <= 0:
            return False

        # Escalar imagen para "cover" (llenar y recortar centro)
        img = self._bg_pil
        src_w, src_h = img.size
        scale = max(width / src_w, height / src_h)
        new_w = max(1, int(src_w * scale))
        new_h = max(1, int(src_h * scale))
        resized = img.resize((new_w, new_h), Image.LANCZOS)

        # Recortar al centro
        left = (new_w - width) // 2
        top = (new_h - height) // 2
        cropped = resized.crop((left, top, left + width, top + height))

        # Convertir a PhotoImage para tkinter y guardar referencia
        try:
            self._bg_tk = ImageTk.PhotoImage(cropped)
        except Exception:
            return False

        # Dibujar en canvas
        try:
            canvas.delete(tag)
        except Exception:
            pass
        canvas.create_image(0, 0, image=self._bg_tk, anchor="nw", tags=(tag,))
        # Enviar al fondo
        try:
            canvas.lower(tag)
        except Exception:
            pass
        return True

    # ================ Avatar drawing ================
    def draw_avatar(self, canvas, x: float, y: float, size: float, seed: Optional[int] = None, with_border: Optional[bool] = None):
        """
        Dibuja un avatar sencillo (círculo cabeza, ojos y boca) centrado en (x,y) sobre el canvas.
        
        Parámetros:
        - canvas: tkinter.Canvas donde dibujar.
        - x, y: coordenadas del centro del avatar.
        - size: diámetro del "rostro".
        - seed: entero para determinismo en la selección de color/rasgos. Si es None usa aleatorio.
        - with_border: anula self.default_with_border si no es None.
        """
        try:
            rnd = random.Random(seed) if seed is not None else random
        except Exception:
            rnd = random

        body_color = rnd.choice(self.colors)
        eye_color = "black"
        border = self.default_with_border if with_border is None else with_border

        r = size / 2
        left = x - r
        top = y - r
        right = x + r
        bottom = y + r
        canvas.create_oval(left, top, right, bottom, fill=body_color, outline=("black" if border else body_color), width=2 if border else 0)

        eye_w = size * 0.12
        eye_h = size * 0.12
        eye_x_offset = size * 0.2
        eye_y = y - size * 0.08
        canvas.create_oval(x - eye_x_offset - eye_w/2, eye_y - eye_h/2, x - eye_x_offset + eye_w/2, eye_y + eye_h/2, fill=eye_color)
        canvas.create_oval(x + eye_x_offset - eye_w/2, eye_y - eye_h/2, x + eye_x_offset + eye_w/2, eye_y + eye_h/2, fill=eye_color)

        mouth_w = size * 0.4
        mouth_h = size * 0.15
        mouth_y = y + size * 0.18
        style = rnd.choice(["smile", "line", "surprised"])
        if style == "smile":
            canvas.create_arc(x - mouth_w/2, mouth_y - mouth_h/2, x + mouth_w/2, mouth_y + mouth_h/2, start=200, extent=140, style="arc", width=2)
        elif style == "surprised":
            canvas.create_oval(x - mouth_h/2, mouth_y - mouth_h/2, x + mouth_h/2, mouth_y + mouth_h/2, fill="black")
        else:
            canvas.create_line(x - mouth_w/2, mouth_y, x + mouth_w/2, mouth_y, width=2)

    def make_avatar_canvas(self, parent, size: int, seed: Optional[int] = None):
        """
        Crea y devuelve un tkinter.Canvas con el avatar dibujado.
        
        Parámetros:
        - parent: widget parent de tkinter para el canvas.
        - size: tamaño (ancho y alto) del canvas en píxeles.
        - seed: entero para determinismo del avatar.
        
        Devuelve:
        - Canvas con el avatar dibujado, o None si no se pudo crear.
        """
        try:
            from tkinter import Canvas
        except Exception:
            return None
        c = Canvas(parent, width=size, height=size, highlightthickness=0, bg=self.bg)
        self.draw_avatar(c, size/2, size/2, size, seed=seed)
        return c


# ================ Instancia por defecto (compatibilidad) ================
_default_graficos = Graficos()

def draw_avatar(canvas, x, y, size, seed=None, with_border=None):
    """Función de conveniencia que delega en la instancia por defecto."""
    return _default_graficos.draw_avatar(canvas, x, y, size, seed=seed, with_border=with_border)

def make_avatar_canvas(parent, size, seed=None):
    """Función de conveniencia que delega en la instancia por defecto."""
    return _default_graficos.make_avatar_canvas(parent, size, seed=seed)

def set_background(path: str) -> bool:
    """Conveniencia: carga background en la instancia por defecto."""
    return _default_graficos.set_background(path)

def draw_background(canvas, width: Optional[int] = None, height: Optional[int] = None, tag: str = "bg") -> bool:
    """Conveniencia: dibuja background en la instancia por defecto."""
    return _default_graficos.draw_background(canvas, width=width, height=height, tag=tag)

def clear_background():
    """Conveniencia: elimina background de la instancia por defecto."""
    return _default_graficos.clear_background()