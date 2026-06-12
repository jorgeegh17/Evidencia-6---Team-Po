"""
CNH Aftermarket Intelligence — Launcher
Interfaz gráfica para instalar dependencias y lanzar el dashboard.
Compatible con ejecución directa (.py) y como .exe compilado (PyInstaller).
"""

import tkinter as tk
from tkinter import messagebox
import subprocess, sys, os, threading, webbrowser, time, importlib.util



# ── Ruta base: funciona tanto en .py como en .exe (PyInstaller) ─
if getattr(sys, 'frozen', False):
    BASE = sys._MEIPASS
    DIST = os.path.dirname(sys.executable)
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    DIST = BASE

DASHBOARD = os.path.join(BASE, "app.py")
URL       = "http://127.0.0.1:8050"

# ── Paleta CNH ─────────────────────────────────────────────────
BG     = "#1C1A21"
CARD   = "#221F28"
BORDER = "#3A3640"
ROJO   = "#900C0E"
ROJO2  = "#C1121F"
BLANCO = "#EDECEC"
GRIS   = "#9797A0"
GRIS2  = "#4A4550"
VERDE  = "#06D6A0"
AMBAR  = "#FFB703"

LIBRERIAS = {
    "dash":                      "dash",
    "dash-bootstrap-components": "dash_bootstrap_components",
    "plotly":                    "plotly",
    "pandas":                    "pandas",
    "numpy":                     "numpy",
    "openpyxl":                  "openpyxl",
    "flask":                     "flask",
    "statsmodels":               "statsmodels",
}

def get_python():
    if getattr(sys, 'frozen', False):
        import shutil
        for cmd in ["py", "python", "python3"]:
            path = shutil.which(cmd)
            if path and "meipass" not in path.lower():
                return path
        return "python"
    return sys.executable

def faltantes():
    return [pip for pip, mod in LIBRERIAS.items()
            if importlib.util.find_spec(mod) is None]


class App:
    def __init__(self, root):
        self.root = root
        self.proc = None

        self._build()

        #self.root.after(100, self._show_splash)
        self._check_env()

    # ── UI ─────────────────────────────────────────────────────
    def _build(self):
        r = self.root
        r.title("CNH Aftermarket Intelligence")
        r.configure(bg=BG)
        r.resizable(False, False)
        w, h = 460, 500   # un poco más alto para el botón extra
        sx, sy = r.winfo_screenwidth(), r.winfo_screenheight()
        r.geometry(f"{w}x{h}+{(sx-w)//2}+{(sy-h)//2}")

        # Ícono de la ventana
        ico = os.path.join(BASE, "cnh.ico")
        if os.path.exists(ico):
            try: r.iconbitmap(ico)
            except: pass

        # Franja roja superior
        tk.Frame(r, bg=ROJO, height=4).pack(fill="x")

        # Header
        hdr = tk.Frame(r, bg=BG, pady=24)
        hdr.pack(fill="x")
        tk.Label(hdr, text="CNH", bg=BG, fg=ROJO,
                 font=("Segoe UI", 30, "bold")).pack()
        tk.Label(hdr, text="AFTERMARKET INTELLIGENCE",
                 bg=BG, fg=BLANCO,
                 font=("Segoe UI", 10, "bold")).pack()
        tk.Label(hdr, text="Dashboard Launcher",
                 bg=BG, fg=GRIS,
                 font=("Segoe UI", 9)).pack(pady=(3, 0))

        tk.Frame(r, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(10, 0))

        # Zona de estado
        estado = tk.Frame(r, bg=BG, pady=20)
        estado.pack(fill="x", padx=30)

        self.ico_var = tk.StringVar(value="⏳")
        self.msg_var = tk.StringVar(value="Verificando entorno…")
        self.sub_var = tk.StringVar(value="")

        self.ico_lbl = tk.Label(estado, textvariable=self.ico_var,
                                bg=BG, fg=AMBAR,
                                font=("Segoe UI", 22))
        self.ico_lbl.pack()

        self.msg_lbl = tk.Label(estado, textvariable=self.msg_var,
                                bg=BG, fg=BLANCO,
                                font=("Segoe UI", 11, "bold"),
                                wraplength=380, justify="center")
        self.msg_lbl.pack(pady=(6, 2))

        self.sub_lbl = tk.Label(estado, textvariable=self.sub_var,
                                bg=BG, fg=GRIS,
                                font=("Segoe UI", 9),
                                wraplength=380, justify="center")
        self.sub_lbl.pack()

        tk.Frame(r, bg=BORDER, height=1).pack(fill="x", padx=30, pady=(4, 0))

        # Barra de progreso (oculta por defecto)
        self.prog_frame = tk.Frame(r, bg=BG, pady=6)
        self.prog_lbl   = tk.Label(self.prog_frame, text="",
                                   bg=BG, fg=GRIS,
                                   font=("Consolas", 8))
        self.prog_lbl.pack()
        self.prog_canvas = tk.Canvas(self.prog_frame, bg=CARD,
                                     height=4, highlightthickness=0)
        self.prog_canvas.pack(fill="x", padx=30)

        # Botones
        btns = tk.Frame(r, bg=BG, padx=30, pady=14)
        btns.pack(fill="x")

        self.btn_main = self._btn(btns, "Verificando…", self._noop,
                                  bg=GRIS2, fg=GRIS, state="disabled")
        self.btn_main.pack(fill="x", ipady=12, pady=(0, 8))

        # Botón desinstalar (oculto hasta que las deps estén instaladas)
        self.btn_uninstall = self._btn(
            btns, "🗑  Desinstalar librerias", self._desinstalar,
            bg=CARD, fg=GRIS, hover=BORDER)
        # No se hace .pack() aquí; se muestra/oculta dinámicamente

        self.btn_close = self._btn(btns, "✕  Cerrar", self._cerrar,
                                   bg=CARD, fg=GRIS, hover=BORDER)
        self.btn_close.pack(fill="x", ipady=8)

        # Footer
        tk.Frame(r, bg=BORDER, height=1).pack(fill="x", side="bottom")
        tk.Label(r, text=f"Python {sys.version.split()[0]}  •  {URL}",
                 bg=BG, fg=GRIS2, font=("Segoe UI", 8),
                 pady=7).pack(side="bottom", fill="x")

    def _btn(self, parent, text, cmd,
             bg=ROJO, fg=BLANCO, hover=ROJO2, state="normal"):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=bg, fg=fg, font=("Segoe UI", 10, "bold"),
                      relief="flat", bd=0, cursor="hand2",
                      activebackground=hover, activeforeground=fg,
                      state=state)
        b.bind("<Enter>", lambda e: b.config(bg=hover)
               if str(b["state"]) == "normal" else None)
        b.bind("<Leave>", lambda e: b.config(bg=bg)
               if str(b["state"]) == "normal" else None)
        return b

    # ── Helpers de UI (thread-safe) ────────────────────────────
    def _noop(self): pass

    def _show_uninstall_btn(self, visible):
        """Muestra u oculta el botón de desinstalar."""
        def _do():
            if visible:
                self.btn_uninstall.pack(fill="x", ipady=8, pady=(0, 8),
                                        before=self.btn_close)
            else:
                self.btn_uninstall.pack_forget()
        self.root.after(0, _do)

    def _set_estado(self, ico, ico_color, msg, sub,
                    btn_text, btn_cmd, btn_bg=ROJO, btn_hover=ROJO2,
                    btn_state="normal", btn_fg=BLANCO,
                    show_uninstall=False):
        def _do():
            self.ico_var.set(ico)
            self.msg_var.set(msg)
            self.sub_var.set(sub)
            self.ico_lbl.config(fg=ico_color)

            cfg = dict(text=btn_text,
                       command=btn_cmd or self._noop,
                       state=btn_state,
                       fg=btn_fg,
                       bg=btn_bg if btn_state == "normal" else GRIS2,
                       activebackground=btn_hover)
            self.btn_main.config(**cfg)
            self.btn_main.bind("<Enter>",
                lambda e: self.btn_main.config(bg=btn_hover)
                if str(self.btn_main["state"]) == "normal" else None)
            self.btn_main.bind("<Leave>",
                lambda e: self.btn_main.config(bg=btn_bg)
                if str(self.btn_main["state"]) == "normal" else None)
        self.root.after(0, _do)
        self._show_uninstall_btn(show_uninstall)

    def _show_progress(self, visible):
        def _do():
            if visible:
                self.prog_frame.pack(after=self.sub_lbl.master,
                                     fill="x", padx=0)
            else:
                self.prog_frame.pack_forget()
        self.root.after(0, _do)

    def _draw_bar(self, fraction):
        def _do():
            c = self.prog_canvas
            c.delete("all")
            c.update_idletasks()
            W = c.winfo_width()
            if W > 1:
                c.create_rectangle(0, 0, int(W * fraction), 4,
                                   fill=ROJO, outline="")
        self.root.after(0, _do)

    # ── Lógica principal ───────────────────────────────────────
    def _check_env(self):
        threading.Thread(target=self._check_thread, daemon=True).start()

    def _check_thread(self):
        python = get_python()
        miss = []
        for pip, mod in LIBRERIAS.items():
            r = subprocess.run(
                [python, "-c", f"import {mod}"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            if r.returncode != 0:
                miss.append(pip)

        if miss:
            self._set_estado(
                ico="⚠", ico_color=AMBAR,
                msg="Faltan librerias",
                sub=f"Se necesitan instalar {len(miss)} libreria(s) antes de continuar.",
                btn_text="⬇  Instalar librerias", btn_cmd=self._instalar,
                show_uninstall=False,
            )
        else:
            self._set_estado(
                ico="✓", ico_color=VERDE,
                msg="Todo listo",
                sub="Las librerias estan instaladas.\nPuedes lanzar el dashboard.",
                btn_text="▶  Lanzar Dashboard", btn_cmd=self._lanzar,
                show_uninstall=True,   # ← aparece el botón de desinstalar
            )

    def _instalar(self):
        self._set_estado(
            ico="⏳", ico_color=AMBAR,
            msg="Instalando librerias…",
            sub="Esto puede tardar un minuto.\nNo cierres esta ventana.",
            btn_text="Instalando…", btn_cmd=None, btn_state="disabled",
            show_uninstall=False,
        )
        self._show_progress(True)
        threading.Thread(target=self._instalar_thread, daemon=True).start()

    def _instalar_thread(self):
        libs  = list(LIBRERIAS.keys())
        total = len(libs)
        for i, lib in enumerate(libs):
            self.root.after(0, lambda l=lib, n=i:
                self.prog_lbl.config(
                    text=f"Instalando {l}  ({n+1}/{total})"))
            self._draw_bar((i + 0.5) / total)

            if importlib.util.find_spec(LIBRERIAS[lib]) is not None:
                self._draw_bar((i + 1) / total)
                continue
            r = subprocess.run(
                [get_python(), "-m", "pip", "install", lib, "--quiet"],
                capture_output=True, text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

            if r.returncode != 0:
                self._show_progress(False)
                self._set_estado(
                    ico="✗", ico_color=ROJO2,
                    msg="Error en la instalación",
                    sub=f"No se pudo instalar «{lib}».\nVerifica tu conexión a internet e inténtalo de nuevo.",
                    btn_text="⟳  Reintentar", btn_cmd=self._instalar,
                    show_uninstall=False,
                )
                return
            self._draw_bar((i + 1) / total)

        self._show_progress(False)
        self._set_estado(
            ico="✓", ico_color=VERDE,
            msg="Instalación completa",
            sub="Todas las librerias están listas.",
            btn_text="▶  Lanzar Dashboard", btn_cmd=self._lanzar,
            show_uninstall=True,   # ← aparece el botón de desinstalar
        )

    def _lanzar(self):
        if not os.path.exists(DASHBOARD):
            messagebox.showerror(
                "Archivo no encontrado",
                f"No se encontró app.py\nRuta: {BASE}")
            return

        self._set_estado(
            ico="⏳", ico_color=AMBAR,
            msg="Iniciando servidor…",
            sub="El navegador se abrirá automáticamente\nen unos segundos.",
            btn_text="Iniciando…", btn_cmd=None, btn_state="disabled",
            show_uninstall=False,
        )

        flags = 0
        if sys.platform == "win32":
            flags = subprocess.CREATE_NO_WINDOW

        self.proc = subprocess.Popen(
            [get_python(), DASHBOARD],
            cwd=BASE, creationflags=flags)

        def _open():
            time.sleep(10)
            webbrowser.open(URL)
            self._set_estado(
                ico="▶", ico_color=VERDE,
                msg="Dashboard corriendo",
                sub=f"Abierto en tu navegador\n{URL}",
                btn_text="■  Detener Dashboard", btn_cmd=self._detener,
                btn_bg=CARD, btn_hover=BORDER, btn_fg=ROJO2,
                show_uninstall=False,  # no desinstalar mientras corre
            )
        threading.Thread(target=_open, daemon=True).start()

    def _detener(self):
        if self.proc:

            try:
                subprocess.run(
                    [
                        "taskkill",
                        "/F",
                        "/T",
                        "/PID",
                        str(self.proc.pid)
                    ],
                    capture_output=True
                )
            except:
                pass

            self.proc = None

        self._set_estado(
            ico="■",
            ico_color=GRIS,
            msg="Dashboard detenido",
            sub="Puedes volver a lanzarlo cuando quieras.",
            btn_text="▶ Lanzar Dashboard",
            btn_cmd=self._lanzar,
            show_uninstall=True,
        )

    # ── Desinstalar dependencias ───────────────────────────────
    def _desinstalar(self):
        confirmar = messagebox.askyesno(
            "Desinstalar librerias de analitica",
            "¿Seguro que deseas desinstalar las librerías del dashboard?\n\n"
            "• dash\n• dash-bootstrap-components\n• plotly\n"
            "• pandas\n• numpy\n• openpyxl\n\n"
            "Tendrás que reinstalarlas para volver a usar la app."
        )
        if not confirmar:
            return

        self._set_estado(
            ico="⏳", ico_color=AMBAR,
            msg="Desinstalando librerias…",
            sub="No cierres esta ventana.",
            btn_text="Desinstalando…", btn_cmd=None, btn_state="disabled",
            show_uninstall=False,
        )
        self._show_progress(True)
        threading.Thread(target=self._desinstalar_thread, daemon=True).start()

    def _desinstalar_thread(self):
        libs  = list(LIBRERIAS.keys())
        total = len(libs)
        for i, lib in enumerate(libs):
            self.root.after(0, lambda l=lib, n=i:
                self.prog_lbl.config(
                    text=f"Eliminando {l}  ({n+1}/{total})"))
            self._draw_bar((i + 0.5) / total)

            subprocess.run(
                [get_python(), "-m", "pip", "uninstall", lib, "-y", "--quiet"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            self._draw_bar((i + 1) / total)

        self._show_progress(False)
        self._set_estado(
            ico="🗑", ico_color=GRIS,
            msg="librerias eliminadas",
            sub="Las librerías han sido desinstaladas.\nInstálalas de nuevo para usar el dashboard.",
            btn_text="⬇  Instalar librerias", btn_cmd=self._instalar,
            show_uninstall=False,
        )

    def _cerrar(self):

        self._detener()
        self.root.destroy()

if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    root = tk.Tk()
    app  = App(root)
    root.protocol("WM_DELETE_WINDOW", app._cerrar)
    root.mainloop()