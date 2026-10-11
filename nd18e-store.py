#!/usr/bin/env python3
# ND18E Sklep - instalowanie i usuwanie aplikacji jednym klikniem (Flathub).
import tkinter as tk
from tkinter import ttk
import subprocess, threading, queue
import configparser, os


def load_palette():
    """Kolory zgodne z trybem wybranym w Ustawieniach (Motyw): ciemny (czarny) albo jasny."""
    cp = configparser.RawConfigParser(strict=False, delimiters=("=",))
    try:
        cp.read(os.path.expanduser("~/.config/lxqt/lxqt.conf"), encoding="utf-8")
        light = cp.get("General", "theme").strip().lower() == "light"
    except Exception:
        light = False
    if light:
        return dict(BG="#f3f3f5", FG="#161616", PANEL="#ffffff", DIM="#5c5c5c", BTN="#d9d9de", BTNH="#c7c7ce",
                    LINE="#b8b8c0", OK="#15803d", BAD="#c62828", LOGBG="#ffffff", LOGFG="#0b6a2b")
    return dict(BG="#0a0a0a", FG="#f2f2f2", PANEL="#161616", DIM="#9a9a9a", BTN="#2a2a2a", BTNH="#3a3a3a",
                LINE="#3a3a3a", OK="#4ade80", BAD="#ff6b5e", LOGBG="#050505", LOGFG="#7dff9a")


P = load_palette()
BG, FG, PANEL, DIM, BTN, BTNH, LINE, OK, BAD, LOGBG, LOGFG = (
    P[k] for k in ("BG", "FG", "PANEL", "DIM", "BTN", "BTNH", "LINE", "OK", "BAD", "LOGBG", "LOGFG"))
RED = "#e11d2e"
APPS = [("Firefox", "org.mozilla.firefox", "Przegladarka"), ("Chromium", "org.chromium.Chromium", "Przegladarka"),
        ("Steam", "com.valvesoftware.Steam", "Gry"),
        ("Minecraft Launcher", "com.mojang.Minecraft", "Minecraft Java"),
        ("Prism Launcher", "org.prismlauncher.PrismLauncher", "Minecraft z modami"), ("Lutris", "net.lutris.Lutris", "Gry z Windowsa"),
        ("Discord", "com.discordapp.Discord", "Czat"), ("OBS Studio", "com.obsproject.Studio", "Nagrywanie i stream"),
        ("VLC", "org.videolan.VLC", "Filmy i muzyka"), ("Spotify", "com.spotify.Client", "Muzyka"),
        ("GIMP", "org.gimp.GIMP", "Grafika"), ("Blender", "org.blender.Blender", "Grafika 3D"),
        ("Audacity", "org.audacityteam.Audacity", "Edycja dzwieku"), ("LibreOffice", "org.libreoffice.LibreOffice", "Biuro")]


def fade_in(w, step=0.08, delay=15):
    """Plynne pojawianie sie okna (wymaga kompozytora - picom)."""
    try:
        w.attributes("-alpha", 0.0)
    except tk.TclError:
        return

    def f(a=0.0):
        a = min(1.0, a + step)
        try:
            w.attributes("-alpha", a)
        except tk.TclError:
            return
        if a < 1.0:
            w.after(delay, f, a)
    f()


def hov(b, c1, c2):
    """Zmiana koloru przycisku po najechaniu myszka."""
    b.bind("<Enter>", lambda e: b.config(bg=c2))
    b.bind("<Leave>", lambda e: b.config(bg=c1))
    return b


class Store(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E Sklep")
        s.geometry("640x540")
        s.configure(bg=BG)
        s.q, s.busy, s.inst = queue.Queue(), False, set()
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=30, borderwidth=0)
        st.configure("Treeview.Heading", background=BTN, foreground=FG)
        st.map("Treeview", background=[("selected", RED)], foreground=[("selected", "white")])
        tk.Label(s, text="Sklep z aplikacjami", bg=BG, fg=RED, font=("sans", 16, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        s.sv = tk.StringVar()
        s.sv.trace_add("write", lambda *a: s.fill())
        tk.Entry(s, textvariable=s.sv, bg=PANEL, fg=FG, insertbackground=FG, relief="flat").pack(fill="x", padx=12, pady=6, ipady=6)
        s.tv = ttk.Treeview(s, columns=("n", "d", "s"), show="headings", selectmode="browse", height=10)
        for c, t, w in (("n", "Aplikacja", 190), ("d", "Opis", 260), ("s", "Stan", 130)):
            s.tv.heading(c, text=t)
            s.tv.column(c, width=w)
        s.tv.pack(fill="both", expand=True, padx=12)
        bf = tk.Frame(s, bg=BG)
        bf.pack(fill="x", padx=12, pady=8)
        s.bi = tk.Button(bf, text="Zainstaluj", bg=RED, fg="white", relief="flat", padx=16, pady=6, command=lambda: s.act("install"))
        s.bu = tk.Button(bf, text="Odinstaluj", bg=BTN, fg=FG, relief="flat", padx=16, pady=6, command=lambda: s.act("uninstall"))
        hov(s.bi, RED, "#ff2d40")
        hov(s.bu, BTN, BTNH)
        s.bi.pack(side="left")
        s.bu.pack(side="left", padx=8)
        s.lg = tk.Text(s, height=7, bg=LOGBG, fg=LOGFG, relief="flat", font=("monospace", 9))
        s.lg.pack(fill="x", padx=12, pady=(0, 12))
        s.fill()
        s.run(["flatpak", "list", "--app", "--columns=application"], quiet=True)
        s.after(150, s.poll)
        fade_in(s)

    def fill(s):
        f = s.sv.get().lower()
        s.tv.delete(*s.tv.get_children())
        for n, i, d in APPS:
            if f in n.lower() or f in d.lower():
                s.tv.insert("", "end", iid=i, values=(n, d, "Zainstalowana" if i in s.inst else ""))

    def act(s, what):
        sel = s.tv.selection()
        if not sel or s.busy:
            return
        app = sel[0]
        if what == "install":
            cmd = ["sh", "-c", "flatpak remote-add --user --if-not-exists flathub "
                   "https://flathub.org/repo/flathub.flatpakrepo && "
                   "flatpak install --user -y --noninteractive flathub " + app]
        else:
            cmd = ["flatpak", "uninstall", "--user", "-y", "--noninteractive", app]
        s.lg.insert("end", "> " + " ".join(cmd) + "\n")
        s.run(cmd)

    def run(s, cmd, quiet=False):
        s.busy = True
        s.bi.config(state="disabled")
        s.bu.config(state="disabled")

        def w():
            out = []
            try:
                p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in p.stdout:
                    out.append(line.strip())
                    if not quiet:
                        s.q.put(("log", line))
                p.wait()
                s.q.put(("done", p.returncode, out, quiet))
            except Exception as e:
                s.q.put(("log", str(e) + "\n"))
                s.q.put(("done", 1, [], quiet))
        threading.Thread(target=w, daemon=True).start()

    def poll(s):
        while not s.q.empty():
            m = s.q.get()
            if m[0] == "log":
                s.lg.insert("end", m[1])
                s.lg.see("end")
            else:
                s.busy = False
                s.bi.config(state="normal")
                s.bu.config(state="normal")
                if m[3]:
                    s.inst = set(m[2])
                    s.fill()
                else:
                    if m[1] == 0:
                        subprocess.Popen(["paplay", "/usr/share/sounds/nd18e/done.wav"])
                    s.run(["flatpak", "list", "--app", "--columns=application"], quiet=True)
        s.after(150, s.poll)


Store().mainloop()
