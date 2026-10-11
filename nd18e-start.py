#!/usr/bin/env python3
# ND18E Menu Start - jak w Windowsie: wyszukiwarka aplikacji, lista aplikacji i boczna ramka
# (Menedzer plikow, Ustawienia systemu, Wylacz). Najechanie na "Wylacz" otwiera mala ramke:
# Wylacz komputer / Uruchom ponownie / Wyloguj. Otwierane literka "N" na pasku (lub klawiszem Super).
import tkinter as tk
import configparser, glob, os, re, shlex, signal, subprocess, sys, time


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
                    LINE="#b8b8c0")
    return dict(BG="#0a0a0a", FG="#f2f2f2", PANEL="#161616", DIM="#9a9a9a", BTN="#2a2a2a", BTNH="#3a3a3a",
                LINE="#3a3a3a")


P = load_palette()
BG, FG, PANEL, DIM, BTN, BTNH, LINE = (P[k] for k in ("BG", "FG", "PANEL", "DIM", "BTN", "BTNH", "LINE"))
RED = "#e11d2e"

HOME = os.path.expanduser("~")
RT = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
PIDF = os.path.join(RT, "nd18e-start.pid")
TSF = os.path.join(RT, "nd18e-start.closed")
LANG = (os.environ.get("LANG") or "en")[:2]
DIRS = [HOME + "/.local/share/applications", HOME + "/.local/share/flatpak/exports/share/applications",
        "/var/lib/flatpak/exports/share/applications", "/usr/local/share/applications", "/usr/share/applications"]


def alive(pid):
    try:
        os.kill(pid, 0)
        return b"nd18e-start" in open("/proc/%d/cmdline" % pid, "rb").read()
    except Exception:
        return False


def toggle_guard():
    """Drugie klikniecie w "N" zamyka otwarte menu zamiast otwierac drugie."""
    try:
        if time.time() - float(open(TSF).read()) < 0.6:
            sys.exit(0)
    except (OSError, ValueError):
        pass
    try:
        pid = int(open(PIDF).read())
        if pid != os.getpid() and alive(pid):
            os.kill(pid, signal.SIGTERM)
            sys.exit(0)
    except (OSError, ValueError):
        pass
    try:
        open(PIDF, "w").write(str(os.getpid()))
    except OSError:
        pass


def panel_geom():
    cp = configparser.RawConfigParser(strict=False, delimiters=("=",))
    try:
        cp.read(os.path.expanduser("~/.config/lxqt/panel.conf"), encoding="utf-8")
        return int(cp.get("panel1", "panelSize")), cp.get("panel1", "position")
    except Exception:
        return 44, "Bottom"


def parse_desktop(path):
    d, inside = {}, False
    try:
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("["):
                if inside:
                    break
                inside = line == "[Desktop Entry]"
                continue
            if inside and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                d.setdefault(k.strip(), v.strip())
    except Exception:
        return None
    return d


def load_apps():
    seen, apps = set(), []
    for dd in DIRS:
        for f in sorted(glob.glob(dd + "/*.desktop")):
            bid = os.path.basename(f)
            if bid in seen:
                continue
            seen.add(bid)
            d = parse_desktop(f)
            if not d or d.get("Type", "Application") != "Application" or not d.get("Exec"):
                continue
            if d.get("NoDisplay", "").lower() == "true" or d.get("Hidden", "").lower() == "true":
                continue
            only = d.get("OnlyShowIn")
            if only and "LXQt" not in only.split(";"):
                continue
            if bid.startswith("nd18e-start"):
                continue
            name = d.get("Name[%s]" % LANG) or d.get("Name")
            if not name:
                continue
            extra = " ".join((d.get("GenericName", ""), d.get("Keywords", ""), d.get("Comment", ""))).lower()
            apps.append({"name": name, "exec": d["Exec"], "term": d.get("Terminal", "").lower() == "true",
                         "extra": extra})
    apps.sort(key=lambda a: a["name"].lower())
    return apps


def run_exec(app):
    out = []
    try:
        for t in shlex.split(app["exec"]):
            if t in ("@@", "@@u", "@@U"):
                continue
            t = re.sub(r"%[fFuUdDnNickvm]", "", t).replace("%%", "%")
            if t:
                out.append(t)
        if not out:
            return
        if app["term"]:
            out = ["qterminal", "-e"] + out
        subprocess.Popen(out, start_new_session=True, cwd=HOME, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    except Exception:
        pass


def popup(w):
    """Okno bez ramki systemowej; typ popup_menu pozwala kompozytorowi dac cien i zaokraglone rogi."""
    w.overrideredirect(True)
    try:
        w.attributes("-type", "popup_menu")
    except tk.TclError:
        pass


def appear(w, x, y, step=0, n=8):
    """Plynne pojawianie: lekkie wsuniecie z dolu + zanikanie (alpha dziala z kompozytorem picom)."""
    try:
        f = (step + 1) / float(n)
        e = 1 - (1 - f) ** 3
        w.geometry("+%d+%d" % (x, int(y + 14 * (1 - e))))
        w.attributes("-alpha", e)
    except tk.TclError:
        return
    if step < n - 1:
        w.after(14, appear, w, x, y, step + 1, n)


class Start(tk.Tk):
    def __init__(s):
        super().__init__()
        s.closing = False
        s.fly = None
        popup(s)
        try:
            s.attributes("-alpha", 0.0)
        except tk.TclError:
            pass
        s.configure(bg=LINE)
        sw, sh = s.winfo_screenwidth(), s.winfo_screenheight()
        ph, pos = panel_geom()
        W, H = 640, max(300, min(560, sh - ph - 30))
        s.x = 8
        s.y = ph + 8 if pos == "Top" else sh - ph - H - 8
        s.geometry("%dx%d+%d+%d" % (W, H, s.x, s.y + 14))
        s.apps = load_apps()
        s.shown = []

        body = tk.Frame(s, bg=BG)
        body.pack(fill="both", expand=True, padx=1, pady=1)
        side = tk.Frame(body, bg=PANEL, width=190)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)
        main = tk.Frame(body, bg=BG)
        main.pack(side="left", fill="both", expand=True)

        # --- lewa strona: naglowek, wyszukiwarka, lista aplikacji
        top = tk.Frame(main, bg=BG)
        top.pack(fill="x", padx=16, pady=(14, 8))
        tk.Label(top, text="N", bg=BG, fg=RED, font=("sans", 22, "bold")).pack(side="left")
        tk.Label(top, text="ND18E", bg=BG, fg=DIM, font=("sans", 11)).pack(side="left", padx=8, pady=(8, 0))
        s.sv = tk.StringVar()
        s.sv.trace_add("write", lambda *a: s.fill())
        s.entry = tk.Entry(main, textvariable=s.sv, bg=PANEL, fg=FG, insertbackground=FG, relief="flat",
                           font=("sans", 13), highlightthickness=0)
        s.entry.pack(fill="x", padx=16, ipady=9)
        tk.Frame(main, bg=RED, height=2).pack(fill="x", padx=16)
        s.hdr = tk.Label(main, text="Wszystkie aplikacje", bg=BG, fg=DIM, anchor="w", font=("sans", 10))
        s.hdr.pack(fill="x", padx=18, pady=(10, 2))
        s.lb = tk.Listbox(main, bg=BG, fg=FG, selectbackground=RED, selectforeground="white", relief="flat",
                          highlightthickness=0, bd=0, activestyle="none", exportselection=False, font=("sans", 12))
        s.lb.pack(fill="both", expand=True, padx=(12, 8), pady=(0, 10))
        s.lb.bind("<Motion>", s.hover)
        s.lb.bind("<ButtonRelease-1>", s.click)

        # --- prawa strona: boczna ramka
        tk.Label(side, text="Szybki dostęp", bg=PANEL, fg=DIM, anchor="w", font=("sans", 10)).pack(
            fill="x", padx=16, pady=(16, 6))
        s.item(side, "Menedżer plików", lambda: s.sh("pcmanfm-qt")).pack(fill="x")
        s.item(side, "Ustawienia systemu", lambda: s.sh("nd18e-setup")).pack(fill="x")
        s.pw = s.item(side, "Wyłącz   ▸", s.show_fly)
        s.pw.pack(side="bottom", fill="x", pady=(0, 10))
        s.pw.bind("<Enter>", lambda e: (s.pw.config(bg=BTNH), s.show_fly()))

        s.entry.bind("<Return>", s.enter)
        s.entry.bind("<Down>", lambda e: s.move(1))
        s.entry.bind("<Up>", lambda e: s.move(-1))
        s.bind("<Escape>", s.close)
        s.bind("<FocusOut>", lambda e: s.after(200, s.chk))
        signal.signal(signal.SIGTERM, lambda *a: s.close())
        s.fill()
        s.after(250, s.tick)
        s.after(20, s.start)

    # ---------------------------------------------------------------- widgety
    def item(s, parent, text, cmd):
        l = tk.Label(parent, text=text, bg=PANEL, fg=FG, anchor="w", font=("sans", 11), padx=16, pady=11,
                     cursor="hand2")
        l.bind("<Enter>", lambda e: l.config(bg=BTNH), add="+")
        l.bind("<Leave>", lambda e: l.config(bg=PANEL))
        l.bind("<Button-1>", lambda e: cmd())
        return l

    def start(s):
        appear(s, s.x, s.y)
        s.focus_force()
        s.entry.focus_set()

    def tick(s):  # budzi petle Tk, zeby sygnal SIGTERM (zamkniecie przez ponowne klikniecie w "N") byl obsluzony
        if not s.closing:
            s.after(250, s.tick)

    def chk(s):
        if not s.closing and s.focus_displayof() is None:
            s.close()

    def close(s, *a):
        if s.closing:
            return
        s.closing = True
        try:
            open(TSF, "w").write(str(time.time()))
            os.remove(PIDF)
        except OSError:
            pass
        s.destroy()

    # ---------------------------------------------------------------- lista
    def fill(s):
        q = s.sv.get().strip().lower()
        if q:
            ranked = []
            for a in s.apps:
                n = a["name"].lower()
                r = 0 if n.startswith(q) else 1 if q in n else 2 if q in a["extra"] else None
                if r is not None:
                    ranked.append((r, n, a))
            ranked.sort(key=lambda t: (t[0], t[1]))
            s.shown = [t[2] for t in ranked]
            s.hdr.config(text="Wyniki wyszukiwania" if s.shown else "Brak wyników")
        else:
            s.shown = list(s.apps)
            s.hdr.config(text="Wszystkie aplikacje")
        s.lb.delete(0, "end")
        for a in s.shown:
            s.lb.insert("end", "   " + a["name"])
        if q and s.shown:
            s.pick(0)

    def pick(s, i, see=True):
        s.lb.selection_clear(0, "end")
        s.lb.selection_set(i)
        s.lb.activate(i)
        if see:
            s.lb.see(i)

    def hover(s, e):
        i = s.lb.nearest(e.y)
        if 0 <= i < len(s.shown):
            s.pick(i, see=False)

    def click(s, e):
        i = s.lb.nearest(e.y)
        if 0 <= i < len(s.shown):
            s.launch(i)

    def move(s, d):
        n = s.lb.size()
        if n:
            cur = s.lb.curselection()
            i = (cur[0] + d) if cur else (0 if d > 0 else n - 1)
            s.pick(max(0, min(n - 1, i)))
        return "break"

    def enter(s, e=None):
        cur = s.lb.curselection()
        if cur:
            s.launch(cur[0])
        elif s.shown:
            s.launch(0)

    def launch(s, i):
        app = s.shown[i]
        s.close()
        run_exec(app)

    # ---------------------------------------------------------------- akcje
    def sh(s, cmd):
        s.close()
        subprocess.Popen(cmd, shell=True, start_new_session=True, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    # ---------------------------------------------------- mala ramka "Wylacz"
    def show_fly(s):
        if s.fly is not None or s.closing:
            return
        f = tk.Toplevel(s)
        popup(f)
        try:
            f.attributes("-alpha", 0.0)
        except tk.TclError:
            pass
        f.configure(bg=LINE)
        inner = tk.Frame(f, bg=PANEL)
        inner.pack(padx=1, pady=1)
        for text, cmd in (("Wyłącz komputer", "lxqt-leave --shutdown || systemctl poweroff"),
                          ("Uruchom ponownie", "lxqt-leave --reboot || systemctl reboot"),
                          ("Wyloguj", "lxqt-leave --logout")):
            s.item(inner, text, lambda c=cmd: s.sh(c)).pack(fill="x")
        f.update_idletasks()
        w, h = max(210, f.winfo_reqwidth()), f.winfo_reqheight()
        x = s.winfo_rootx() + s.winfo_width()
        y = s.pw.winfo_rooty() + s.pw.winfo_height() - h
        f.geometry("%dx%d+%d+%d" % (w, h, x, max(0, y)))
        s.fly = f
        appear(f, x, max(0, y), n=6)
        s.after(250, s.poll_fly)

    def inside(s):
        try:
            w = s.winfo_containing(*s.winfo_pointerxy())
        except Exception:
            return False
        while w is not None:
            if w is s.pw or w is s.fly:
                return True
            w = getattr(w, "master", None)
        return False

    def poll_fly(s):
        if s.closing or s.fly is None:
            return
        if s.inside():
            s.after(150, s.poll_fly)
        else:
            s.fly.destroy()
            s.fly = None
            s.pw.config(bg=PANEL)


if __name__ == "__main__":
    toggle_guard()
    Start().mainloop()
