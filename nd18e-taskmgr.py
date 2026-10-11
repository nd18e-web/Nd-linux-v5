#!/usr/bin/env python3
# ND18E Menedzer zadan - jak w Windowsie: procesy, CPU, pamiec, "Zakoncz zadanie".
import tkinter as tk
from tkinter import ttk
import psutil
from tkinter import messagebox
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


class App(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E Menedzer zadan")
        s.geometry("640x460")
        s.configure(bg=BG)
        s.hist = [0] * 60
        ncpu = psutil.cpu_count() or 1
        s.ncpu = ncpu
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG, rowheight=22, borderwidth=0)
        st.configure("Treeview.Heading", background=BTN, foreground=FG, relief="flat")
        st.map("Treeview", background=[("selected", RED)], foreground=[("selected", "white")])
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background=BTN, foreground=FG, padding=(16, 6))
        st.map("TNotebook.Tab", background=[("selected", RED)], foreground=[("selected", "white")])
        nb = ttk.Notebook(s)
        nb.pack(fill="both", expand=True)

        # --- Procesy ---
        pf = tk.Frame(nb, bg=BG)
        nb.add(pf, text="Procesy")
        s.hdr = tk.Label(pf, bg=BG, fg=FG, anchor="w", font=("sans", 11, "bold"))
        s.hdr.pack(fill="x", padx=8, pady=6)
        cols = ("name", "pid", "cpu", "mem")
        s.tv = ttk.Treeview(pf, columns=cols, show="headings", selectmode="browse")
        for c, t, w in (("name", "Nazwa", 280), ("pid", "PID", 70), ("cpu", "CPU %", 80), ("mem", "Pamiec MB", 100)):
            s.tv.heading(c, text=t)
            s.tv.column(c, width=w, anchor="w" if c == "name" else "e")
        s.tv.pack(fill="both", expand=True, padx=8)
        hov(tk.Button(pf, text="Zakoncz zadanie", bg=RED, fg="white", relief="flat", padx=14, pady=6,
                      command=s.kill), RED, "#ff2d40").pack(anchor="e", padx=8, pady=8)

        # --- Wydajnosc ---
        pe = tk.Frame(nb, bg=BG)
        nb.add(pe, text="Wydajnosc")
        s.info = tk.Label(pe, bg=BG, fg=FG, justify="left", font=("sans", 12))
        s.info.pack(anchor="w", padx=12, pady=12)
        s.cv = tk.Canvas(pe, bg=PANEL, height=170, highlightthickness=1, highlightbackground=LINE)
        s.cv.pack(fill="x", padx=12)
        tk.Label(pe, text="Uzycie procesora (ostatnie ~90 s)", bg=BG, fg=DIM).pack(anchor="w", padx=12)

        psutil.cpu_percent()
        for p in psutil.process_iter():
            try:
                p.cpu_percent()
            except Exception:
                pass
        s.after(1000, s.refresh)
        fade_in(s)

    def kill(s):
        sel = s.tv.selection()
        if not sel:
            return
        name, pid = s.tv.item(sel[0])["values"][:2]
        if not messagebox.askyesno("Zakoncz zadanie", "Zakonczyc proces %s (PID %s)?" % (name, pid)):
            return
        try:
            psutil.Process(int(pid)).terminate()
        except Exception as e:
            messagebox.showerror("Blad", "Nie mozna zakonczyc procesu:\n%s" % e)

    def refresh(s):
        rows = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_info", "cmdline"]):
            i = p.info
            if not i.get("cmdline"):
                continue  # watki jadra systemu nie sa pokazywane (jak w Windowsie)
            try:
                rows.append((i["name"] or "?", i["pid"], (i["cpu_percent"] or 0.0) / s.ncpu, i["memory_info"].rss / 1048576))
            except Exception:
                pass
        rows.sort(key=lambda r: (-r[2], -r[3]))
        keep = s.tv.selection()
        sel_pid = str(s.tv.item(keep[0])["values"][1]) if keep else None
        top = s.tv.yview()[0]
        s.tv.delete(*s.tv.get_children())
        for r in rows:
            iid = s.tv.insert("", "end", values=(r[0], r[1], "%.1f" % r[2], "%.0f" % r[3]))
            if sel_pid is not None and str(r[1]) == sel_pid:
                s.tv.selection_set(iid)
        s.tv.yview_moveto(top)
        cpu = psutil.cpu_percent()
        vm = psutil.virtual_memory()
        s.hdr.config(text="Procesy: %d     CPU: %.0f%%     Pamiec: %.0f%%" % (len(rows), cpu, vm.percent))
        s.info.config(text="Procesor: %.0f%%\nPamiec: %.0f / %.0f MB (%.0f%%)\nLiczba procesow: %d" % (
            cpu, vm.used / 1048576, vm.total / 1048576, vm.percent, len(rows)))
        s.hist = s.hist[1:] + [cpu]
        s.cv.delete("all")
        w, h = s.cv.winfo_width(), s.cv.winfo_height()
        pts = []
        for k, v in enumerate(s.hist):
            pts += [k * w / 59, h - v * h / 100]
        s.cv.create_line(*pts, fill=RED, width=2)
        s.after(1500, s.refresh)


App().mainloop()
