#!/usr/bin/env python3
# ND18E Konfiguracja: kreator pierwszego uruchomienia (--first-run) oraz Ustawienia systemu.
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import subprocess, os, sys, socket, shutil, json, time, glob, configparser

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
MARK = os.path.expanduser("~/.config/nd18e-setup-done")
ANIM = os.path.expanduser("~/.config/nd18e-anim")
DISP = os.path.expanduser("~/.config/nd18e-display")
DPI = os.path.expanduser("~/.config/nd18e-dpi")
AUTO = os.path.expanduser("~/.config/autostart")
LXQT_CONF = os.path.expanduser("~/.config/lxqt/lxqt.conf")
PANEL_CONF = os.path.expanduser("~/.config/lxqt/panel.conf")
PCMAN_CONF = os.path.expanduser("~/.config/pcmanfm-qt/lxqt/settings.conf")
TAB_THEME = 4  # numer zakladki "Motyw" (po przelaczeniu trybu okno otwiera sie od niej)
GTK_CONF = os.path.expanduser("~/.config/gtk-3.0/settings.ini")
WALL_DIR = os.path.expanduser("~/.local/share/backgrounds")
DEFAULT_WALL = "/usr/share/backgrounds/nd18e.png"
PANEL_COLORS = [("Domyślny (z motywu)", None), ("Czerwony", "#a3121e"), ("Czarny", "#0b0b0b"), ("Grafitowy", "#2b2b2b"),
                ("Niebieski", "#1d4ed8"), ("Zielony", "#15803d"), ("Fioletowy", "#6d28d9"), ("Biały", "#f2f2f2")]
SND_OFF = os.path.expanduser("~/.config/nd18e-sounds-off")
ROOT = "/usr/local/bin/nd18e-root"
WIZARD = "--first-run" in sys.argv
START_TAB = next((int(a[6:]) for a in sys.argv if a.startswith("--tab=") and a[6:].isdigit()), 0)
if WIZARD and os.path.exists(MARK):
    sys.exit(0)

# (nazwa, locale, uklad klawiatury)
LANGS = [
    ("Polski", "pl_PL.UTF-8", "pl"), ("English (US)", "en_US.UTF-8", "us"), ("English (UK)", "en_GB.UTF-8", "gb"),
    ("Deutsch", "de_DE.UTF-8", "de"), ("Français", "fr_FR.UTF-8", "fr"), ("Español", "es_ES.UTF-8", "es"),
    ("Italiano", "it_IT.UTF-8", "it"), ("Português (Brasil)", "pt_BR.UTF-8", "br"),
    ("Português (Portugal)", "pt_PT.UTF-8", "pt"), ("Nederlands", "nl_NL.UTF-8", "nl"),
    ("Svenska", "sv_SE.UTF-8", "se"), ("Norsk", "nb_NO.UTF-8", "no"), ("Dansk", "da_DK.UTF-8", "dk"),
    ("Suomi", "fi_FI.UTF-8", "fi"), ("Čeština", "cs_CZ.UTF-8", "cz"), ("Slovenčina", "sk_SK.UTF-8", "sk"),
    ("Magyar", "hu_HU.UTF-8", "hu"), ("Română", "ro_RO.UTF-8", "ro"), ("Български", "bg_BG.UTF-8", "bg"),
    ("Ελληνικά", "el_GR.UTF-8", "gr"), ("Türkçe", "tr_TR.UTF-8", "tr"), ("Русский", "ru_RU.UTF-8", "ru"),
    ("Українська", "uk_UA.UTF-8", "ua"), ("Беларуская", "be_BY.UTF-8", "by"), ("Српски", "sr_RS.UTF-8", "rs"),
    ("Hrvatski", "hr_HR.UTF-8", "hr"), ("Slovenščina", "sl_SI.UTF-8", "si"), ("Lietuvių", "lt_LT.UTF-8", "lt"),
    ("Latviešu", "lv_LV.UTF-8", "lv"), ("Eesti", "et_EE.UTF-8", "ee"), ("Shqip", "sq_AL.UTF-8", "al"),
    ("Македонски", "mk_MK.UTF-8", "mk"), ("Íslenska", "is_IS.UTF-8", "is"), ("Gaeilge", "ga_IE.UTF-8", "ie"),
    ("Català", "ca_ES.UTF-8", "es"), ("Euskara", "eu_ES.UTF-8", "es"), ("Galego", "gl_ES.UTF-8", "es"),
    ("العربية", "ar_SA.UTF-8", "ara"), ("עברית", "he_IL.UTF-8", "il"), ("فارسی", "fa_IR.UTF-8", "ir"),
    ("हिन्दी", "hi_IN.UTF-8", "in"), ("বাংলা", "bn_BD.UTF-8", "bd"), ("ไทย", "th_TH.UTF-8", "th"),
    ("Tiếng Việt", "vi_VN.UTF-8", "vn"), ("Bahasa Indonesia", "id_ID.UTF-8", "us"),
    ("Bahasa Melayu", "ms_MY.UTF-8", "us"), ("日本語", "ja_JP.UTF-8", "jp"), ("한국어", "ko_KR.UTF-8", "kr"),
    ("中文 (简体)", "zh_CN.UTF-8", "cn"), ("中文 (繁體)", "zh_TW.UTF-8", "tw"), ("Қазақша", "kk_KZ.UTF-8", "kz"),
    ("Հայերեն", "hy_AM.UTF-8", "am"), ("ქართული", "ka_GE.UTF-8", "ge"), ("Afrikaans", "af_ZA.UTF-8", "za"),
]


def cfg_get(path, section, key, default=None):
    cp = configparser.RawConfigParser(strict=False, delimiters=("=",))
    cp.optionxform = str
    try:
        cp.read(path, encoding="utf-8")
        return cp.get(section, key)
    except Exception:
        return default


def cfg_set(path, section, key, value):
    """Zapisuje klucz w pliku .conf/.ini (value=None usuwa klucz)."""
    cp = configparser.RawConfigParser(strict=False, delimiters=("=",))
    cp.optionxform = str
    cp.read(path, encoding="utf-8")
    if not cp.has_section(section):
        cp.add_section(section)
    if value is None:
        cp.remove_option(section, key)
    else:
        cp.set(section, key, value)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        cp.write(f, space_around_delimiters=False)


def lum(hexc):
    r, g, b = (int(hexc[i:i + 2], 16) for i in (1, 3, 5))
    return 0.299 * r + 0.587 * g + 0.114 * b


def sh(c):
    try:
        return subprocess.run(c, shell=True, capture_output=True, text=True, timeout=8).stdout.strip()
    except Exception:
        return ""


def xr_modes():
    """(wyjscie, lista trybow, biezacy tryb) pierwszego podlaczonego monitora z xrandr."""
    name, modes, cur = None, [], None
    for line in sh("xrandr 2>/dev/null").splitlines():
        if " connected" in line and name is None:
            name = line.split()[0]
        elif name and line.startswith(" "):
            m = line.split()[0]
            if m not in modes:
                modes.append(m)
            if "*" in line and cur is None:
                cur = m
        elif name and not line.startswith(" "):
            break
    return name, modes, cur


def desktop_info(path):
    """(nazwa, polecenie) z pliku .desktop albo None gdy ukryty / nie-aplikacja."""
    name = exe = None
    try:
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if line.startswith("[") and line != "[Desktop Entry]":
                break
            if line.startswith("Name=") and name is None:
                name = line[5:]
            elif line.startswith("Exec=") and exe is None:
                exe = line[5:]
            elif line in ("NoDisplay=true", "Hidden=true"):
                return None
    except Exception:
        return None
    return (name, exe) if name and exe else None


def online():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=2).close()
        return True
    except Exception:
        return False


def fade_in(w, step=0.08, delay=15):
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
    b.bind("<Enter>", lambda e: b.config(bg=c2))
    b.bind("<Leave>", lambda e: b.config(bg=c1))
    return b


def btn(parent, text, cmd, red=False, **kw):
    c1, c2 = (RED, "#ff2d40") if red else (BTN, BTNH)
    return hov(tk.Button(parent, text=text, command=cmd, bg=c1, fg="white" if red else FG, relief="flat",
                         activebackground=c2, activeforeground="white", bd=0,
                         padx=kw.pop("padx", 16), pady=kw.pop("pady", 7), **kw), c1, c2)


class App(tk.Tk):
    def __init__(s):
        super().__init__()
        s.title("ND18E - Witamy" if WIZARD else "ND18E - Ustawienia systemu")
        s.geometry("920x700")
        s.minsize(680, 560)
        s.configure(bg=BG)
        s.lang_idx = 0
        s.shown = list(range(len(LANGS)))
        s.pin_mode = tk.StringVar(value="skip")
        s.pin1, s.pin2 = tk.StringVar(), tk.StringVar()
        st = ttk.Style(s)
        st.theme_use("clam")
        st.configure("TNotebook", background=BG, borderwidth=0)
        st.configure("TNotebook.Tab", background=BTN, foreground=FG, padding=(9, 7))
        st.map("TNotebook.Tab", background=[("selected", RED)], foreground=[("selected", "white")])
        st.configure("TCombobox", fieldbackground=PANEL, background=BTN, foreground=FG, arrowcolor=FG)
        s.option_add("*TCombobox*Listbox.background", PANEL)
        s.option_add("*TCombobox*Listbox.foreground", FG)
        if WIZARD:
            s.build_wizard()
        else:
            s.build_settings()
        fade_in(s)

    # ---------------------------------------------------------------- strony
    def title_lbl(s, p, text, sub=None):
        tk.Label(p, text=text, bg=BG, fg=FG, font=("sans", 15, "bold")).pack(anchor="w", padx=20, pady=(14, 2))
        if sub:
            tk.Label(p, text=sub, bg=BG, fg=DIM, justify="left", wraplength=640).pack(anchor="w", padx=20)

    def page_lang(s, p, apply_btn=False):
        s.title_lbl(p, "Wybierz swój język", "Zmienia język systemu i układ klawiatury (po ponownym zalogowaniu).")
        s.q = tk.StringVar()
        s.q.trace_add("write", lambda *a: s.fill_langs())
        tk.Entry(p, textvariable=s.q, bg=PANEL, fg=FG, insertbackground=FG, relief="flat").pack(
            fill="x", padx=20, pady=8, ipady=6)
        f = tk.Frame(p, bg=BG)
        f.pack(fill="both", expand=True, padx=20)
        s.lb = tk.Listbox(f, bg=PANEL, fg=FG, selectbackground=RED, selectforeground="white", relief="flat",
                          highlightthickness=0, activestyle="none", font=("sans", 12), exportselection=False)
        sb = tk.Scrollbar(f, command=s.lb.yview)
        s.lb.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        s.lb.pack(side="left", fill="both", expand=True)
        s.lb.bind("<<ListboxSelect>>", s.pick_lang)
        s.fill_langs()
        if apply_btn:
            btn(p, "Zastosuj język", s.apply_lang, red=True).pack(anchor="e", padx=20, pady=10)

    def fill_langs(s):
        q = s.q.get().lower()
        s.shown = [i for i, l in enumerate(LANGS) if q in l[0].lower() or q in l[1].lower()]
        s.lb.delete(0, "end")
        for i in s.shown:
            s.lb.insert("end", LANGS[i][0])
        if s.lang_idx in s.shown:
            k = s.shown.index(s.lang_idx)
            s.lb.selection_set(k)
            s.lb.see(k)

    def pick_lang(s, e=None):
        sel = s.lb.curselection()
        if sel:
            s.lang_idx = s.shown[sel[0]]
            subprocess.Popen(["setxkbmap", LANGS[s.lang_idx][2]], stderr=subprocess.DEVNULL)

    def page_pin(s, p, apply_btn=False):
        s.title_lbl(p, "Ustaw swój PIN",
                    "PIN to numeryczne hasło logowania (4-8 cyfr). Możesz też usunąć hasło albo pominąć ten krok.")
        for v, t in (("set", "Ustaw PIN"), ("remove", "Usuń PIN (logowanie bez hasła)"), ("skip", "Pomiń - nie zmieniaj")):
            tk.Radiobutton(p, text=t, variable=s.pin_mode, value=v, bg=BG, fg=FG, selectcolor=PANEL,
                           activebackground=BG, activeforeground=FG, highlightthickness=0,
                           command=s.pin_state).pack(anchor="w", padx=26, pady=3)
        s.e1 = tk.Entry(p, textvariable=s.pin1, show="•", bg=PANEL, fg=FG, insertbackground=FG, relief="flat",
                        font=("sans", 14), width=14)
        s.e2 = tk.Entry(p, textvariable=s.pin2, show="•", bg=PANEL, fg=FG, insertbackground=FG, relief="flat",
                        font=("sans", 14), width=14)
        tk.Label(p, text="PIN:", bg=BG, fg=DIM).pack(anchor="w", padx=26, pady=(12, 0))
        s.e1.pack(anchor="w", padx=26, ipady=5)
        tk.Label(p, text="Powtórz PIN:", bg=BG, fg=DIM).pack(anchor="w", padx=26, pady=(8, 0))
        s.e2.pack(anchor="w", padx=26, ipady=5)
        s.pin_msg = tk.Label(p, text="", bg=BG, fg=BAD)
        s.pin_msg.pack(anchor="w", padx=26, pady=6)
        s.pin_state()
        if apply_btn:
            btn(p, "Zastosuj", s.apply_pin, red=True).pack(anchor="e", padx=20, pady=10)

    def pin_state(s):
        st = "normal" if s.pin_mode.get() == "set" else "disabled"
        s.e1.config(state=st)
        s.e2.config(state=st)

    def pin_ok(s):
        m = s.pin_mode.get()
        if m == "set":
            a, b = s.pin1.get(), s.pin2.get()
            if not (a.isdigit() and 4 <= len(a) <= 8):
                s.pin_msg.config(text="PIN musi mieć 4-8 cyfr.")
                return False
            if a != b:
                s.pin_msg.config(text="PIN-y nie są takie same.")
                return False
        s.pin_msg.config(text="")
        return True

    def page_look(s, p):
        s.title_lbl(p, "Wygląd i dźwięki", "Mniej animacji = mniejsze obciążenie. Możesz to zmienić w każdej chwili.")
        af = tk.Frame(p, bg=BG)
        af.pack(anchor="w", padx=20, pady=14)
        tk.Label(af, text="Animacje:", bg=BG, fg=FG).pack(side="left", padx=(0, 8))
        s.ab = {}
        for key, name in (("off", "Wyłączone"), ("light", "Lekkie"), ("full", "Pełne")):
            b = tk.Button(af, text=name, command=lambda k=key: s.set_anim(k), relief="flat", bd=0, padx=14, pady=7)
            b.pack(side="left", padx=3)
            s.ab[key] = b
        s.sb = tk.Button(p, command=s.toggle_sounds, relief="flat", bd=0, padx=14, pady=7, bg=BTN, fg=FG)
        s.sb.pack(anchor="w", padx=20, pady=4)
        hov(s.sb, BTN, BTNH)
        btn(p, "Test dźwięku", lambda: subprocess.Popen(["paplay", "/usr/share/sounds/nd18e/startup.wav"])).pack(
            anchor="w", padx=20, pady=10)
        s.paint()

    def cur_anim(s):
        try:
            return open(ANIM).read().strip() or "light"
        except Exception:
            return "light"

    def paint(s):
        cur = s.cur_anim()
        for k, b in s.ab.items():
            b.config(bg=RED if k == cur else BTN, fg="white" if k == cur else FG)
        s.sb.config(text="Dźwięki systemowe: " + ("wyłączone" if os.path.exists(SND_OFF) else "włączone"))

    def set_anim(s, k):
        src = "/etc/xdg/nd18e/picom-%s.conf" % k
        dst = os.path.expanduser("~/.config/picom/picom.conf")
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy(src, dst)
            os.makedirs(os.path.dirname(ANIM), exist_ok=True)
            open(ANIM, "w").write(k)
        except Exception:
            return
        subprocess.Popen("pkill -x picom; sleep 0.3; picom -b || picom -b --backend xrender", shell=True)
        s.paint()

    def toggle_sounds(s):
        os.makedirs(os.path.dirname(SND_OFF), exist_ok=True)
        if os.path.exists(SND_OFF):
            os.remove(SND_OFF)
        else:
            open(SND_OFF, "w").close()
        s.paint()

    def page_hw(s, p):
        s.title_lbl(p, "Sprzęt i internet")
        box = tk.Frame(p, bg=PANEL, highlightthickness=1, highlightbackground=LINE)
        box.pack(fill="x", padx=20, pady=10)

        def row(k, v, ok=None):
            f = tk.Frame(box, bg=PANEL)
            f.pack(fill="x", padx=10, pady=3)
            tk.Label(f, text=k, bg=PANEL, fg=DIM, width=16, anchor="w").pack(side="left")
            tk.Label(f, text=v, bg=PANEL, fg=FG if ok is None else (OK if ok else BAD),
                     anchor="w", justify="left", wraplength=440).pack(side="left", fill="x")
        cpu = sh("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").replace("(R)", "").replace("(TM)", "")
        gpu = sh("lspci | grep -Ei 'vga|3d|display' | head -1 | cut -d: -f3-")
        use = sh("lspci -k | grep -EiA4 'vga|3d' | grep -i 'in use' | head -1 | cut -d: -f2")
        mem = sh("awk '/MemTotal/{printf \"%.1f GB\", $2/1048576}' /proc/meminfo")
        row("Procesor", cpu or "?")
        row("Karta graficzna", gpu or "?")
        row("Pamięć RAM", mem or "?")
        row("Sterownik grafiki", use or "brak")
        if "nvidia" in gpu.lower():
            ok = "nvidia" in use.lower()
            row("NVIDIA", "Sterownik NVIDIA działa" if ok else
                "Używany sterownik otwarty (nouveau). Wyłącz Secure Boot w BIOS i uruchom system ponownie.", ok)
        mc = sh("cat /sys/devices/system/cpu/cpu0/microcode/version 2>/dev/null")
        row("Mikrokod CPU", ("wersja " + mc) if mc else "brak", bool(mc))
        kb = sh("grep -ci 'keyboard' /proc/bus/input/devices")
        ms = sh("grep -ciE 'mouse|touchpad|trackpad' /proc/bus/input/devices")
        row("Klawiatura", "wykryta" if kb not in ("", "0") else "nie wykryto", kb not in ("", "0"))
        row("Mysz / touchpad", "wykryta" if ms not in ("", "0") else "nie wykryto", ms not in ("", "0"))
        snd = sh("aplay -l 2>/dev/null | grep -m1 '^card' | cut -d: -f2-")
        row("Dźwięk", snd.strip() if snd else "brak karty dźwiękowej", bool(snd))
        net = sh("nmcli -t -f DEVICE,TYPE device 2>/dev/null | grep -E 'ethernet|wifi' | tr '\\n' ' '")
        row("Karty sieciowe", net or "nie wykryto", bool(net))
        on = online()
        row("Internet", "połączony" if on else "brak - połącz się z Wi-Fi (ikona przy zegarze)", on)

    # ------------------------------------------------------- czas i strefa
    def page_time(s, p):
        s.title_lbl(p, "Data i godzina", "Strefa czasowa oraz automatyczne ustawianie godziny przez internet.")
        s.tnow = tk.Label(p, bg=BG, fg=FG, font=("sans", 18, "bold"))
        s.tnow.pack(anchor="w", padx=20, pady=(8, 0))
        s.tcur = tk.Label(p, bg=BG, fg=DIM)
        s.tcur.pack(anchor="w", padx=20)
        s.tz = tk.StringVar(value=sh("timedatectl show -p Timezone --value 2>/dev/null"))
        s.ntp = tk.BooleanVar(value=sh("timedatectl show -p NTP --value 2>/dev/null") == "yes")
        tk.Checkbutton(p, text="Ustawiaj godzinę automatycznie (internet)", variable=s.ntp, bg=BG, fg=FG,
                       selectcolor=PANEL, activebackground=BG, activeforeground=FG,
                       highlightthickness=0).pack(anchor="w", padx=20, pady=6)
        s.tzq = tk.StringVar()
        s.tzq.trace_add("write", lambda *a: s.fill_tz())
        tk.Entry(p, textvariable=s.tzq, bg=PANEL, fg=FG, insertbackground=FG, relief="flat").pack(
            fill="x", padx=20, pady=4, ipady=5)
        f = tk.Frame(p, bg=BG)
        f.pack(fill="both", expand=True, padx=20)
        s.tzl = tk.Listbox(f, bg=PANEL, fg=FG, selectbackground=RED, selectforeground="white", relief="flat",
                           highlightthickness=0, activestyle="none", exportselection=False)
        sb = tk.Scrollbar(f, command=s.tzl.yview)
        s.tzl.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        s.tzl.pack(side="left", fill="both", expand=True)
        s.tzl.bind("<<ListboxSelect>>", lambda e: s.tzl.curselection() and s.tz.set(s.tzs[s.tzl.curselection()[0]]))
        s.tzall = sh("timedatectl list-timezones 2>/dev/null").splitlines()
        s.fill_tz()
        btn(p, "Zastosuj", s.apply_time, red=True).pack(anchor="e", padx=20, pady=10)
        s.tick_clock()

    def fill_tz(s):
        q = s.tzq.get().lower()
        s.tzs = [z for z in s.tzall if q in z.lower()]
        s.tzl.delete(0, "end")
        for z in s.tzs:
            s.tzl.insert("end", z)
        if s.tz.get() in s.tzs:
            k = s.tzs.index(s.tz.get())
            s.tzl.selection_set(k)
            s.tzl.see(k)

    def tick_clock(s):
        s.tnow.config(text=time.strftime("%H:%M:%S   %d.%m.%Y"))
        s.tcur.config(text="Wybrana strefa: " + (s.tz.get() or "?"))
        s.after(1000, s.tick_clock)

    def apply_time(s):
        payload = {"ntp": s.ntp.get()}
        if s.tz.get():
            payload["timezone"] = s.tz.get()
        ok = s.run_root(payload)
        messagebox.showinfo("Data i godzina", "Zapisano." if ok else "Nie udało się zapisać zmian (anulowano lub błąd).")

    # ------------------------------------------------------- ekran i tekst
    def page_screen(s, p):
        s.title_lbl(p, "Ekran", "Rozdzielczość monitora i wielkość tekstu.")
        s.out, modes, cur = xr_modes()
        tk.Label(p, text="Monitor: %s" % (s.out or "nie wykryto"), bg=BG, fg=DIM).pack(anchor="w", padx=20, pady=(10, 2))
        s.res = tk.StringVar(value=cur or "")
        s.old_res = cur
        cb = ttk.Combobox(p, textvariable=s.res, values=modes, state="readonly", width=18)
        cb.pack(anchor="w", padx=20, pady=4)
        btn(p, "Zastosuj rozdzielczość", s.apply_res, red=True).pack(anchor="w", padx=20, pady=8)
        tk.Label(p, text="Wielkość tekstu i elementów:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(
            anchor="w", padx=20, pady=(18, 4))
        try:
            cur_dpi = int(open(DPI).read().strip())
        except Exception:
            cur_dpi = 96
        s.dpi = tk.IntVar(value=min((72, 96, 120, 144, 192), key=lambda d: abs(d - cur_dpi)))
        for d, t in ((72, "Mały (75%)"), (96, "Normalny (100%)"), (120, "Większy (125%)"),
                     (144, "Duży (150%)"), (192, "Bardzo duży (200%)")):
            tk.Radiobutton(p, text=t, variable=s.dpi, value=d, bg=BG, fg=FG, selectcolor=PANEL,
                           activebackground=BG, activeforeground=FG, highlightthickness=0).pack(anchor="w", padx=26)
        btn(p, "Zastosuj rozmiar tekstu", s.apply_dpi).pack(anchor="w", padx=20, pady=10)
        s.scr_msg = tk.Label(p, text="", bg=BG, fg=DIM, wraplength=700, justify="left")
        s.scr_msg.pack(anchor="w", padx=20)

    def apply_res(s):
        new = s.res.get()
        if not s.out or not new or new == s.old_res:
            return
        old = s.old_res
        subprocess.run(["xrandr", "--output", s.out, "--mode", new])
        win = tk.Toplevel(s)
        win.title("Zachować rozdzielczość?")
        win.configure(bg=BG)
        win.geometry("360x140")
        lab = tk.Label(win, bg=BG, fg=FG, wraplength=330)
        lab.pack(pady=14)
        state = {"left": 10, "done": False}

        def keep():
            state["done"] = True
            s.old_res = new
            open(DISP, "w").write("%s %s\n" % (s.out, new))
            win.destroy()

        def tick():
            if state["done"]:
                return
            if state["left"] <= 0:
                state["done"] = True
                if old:
                    subprocess.run(["xrandr", "--output", s.out, "--mode", old])
                s.res.set(old or "")
                win.destroy()
                return
            lab.config(text="Zachować rozdzielczość %s?\nPowrót do poprzedniej za %d s." % (new, state["left"]))
            state["left"] -= 1
            win.after(1000, tick)
        btn(win, "Zachowaj", keep, red=True).pack()
        tick()

    def apply_dpi(s):
        d = s.dpi.get()
        os.makedirs(os.path.dirname(DPI), exist_ok=True)
        open(DPI, "w").write(str(d))
        subprocess.run("echo 'Xft.dpi: %d' | xrdb -merge" % d, shell=True)
        s.scr_msg.config(text="Zapisano. Nowy rozmiar zobaczysz w nowo uruchamianych aplikacjach i po ponownym zalogowaniu.")

    # ------------------------------------------------------------ autostart
    def page_auto(s, p):
        s.title_lbl(p, "Autostart", "Programy uruchamiane przy logowaniu. Domyślnie lista jest pusta - "
                    "żadna aplikacja nie startuje sama, dopóki jej tu nie dodasz.")
        tk.Label(p, text="Uruchamiane przy logowaniu:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(
            anchor="w", padx=20, pady=(10, 2))
        s.aul = tk.Listbox(p, bg=PANEL, fg=FG, selectbackground=RED, selectforeground="white", relief="flat",
                           highlightthickness=0, activestyle="none", height=6, exportselection=False)
        s.aul.pack(fill="x", padx=20)
        btn(p, "Usuń z autostartu", s.auto_remove).pack(anchor="w", padx=20, pady=8)
        tk.Label(p, text="Dostępne aplikacje:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(
            anchor="w", padx=20, pady=(6, 2))
        f = tk.Frame(p, bg=BG)
        f.pack(fill="both", expand=True, padx=20)
        s.avl = tk.Listbox(f, bg=PANEL, fg=FG, selectbackground=RED, selectforeground="white", relief="flat",
                           highlightthickness=0, activestyle="none", exportselection=False)
        sb = tk.Scrollbar(f, command=s.avl.yview)
        s.avl.config(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        s.avl.pack(side="left", fill="both", expand=True)
        btn(p, "Dodaj do autostartu", s.auto_add, red=True).pack(anchor="e", padx=20, pady=10)
        s.auto_refresh()

    def auto_refresh(s):
        s.auto_user = []
        s.aul.delete(0, "end")
        for f in sorted(glob.glob(AUTO + "/*.desktop")):
            i = desktop_info(f)
            if i:
                s.auto_user.append(f)
                s.aul.insert("end", i[0])
        s.avail = []
        s.avl.delete(0, "end")
        seen = set()
        dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
                "/var/lib/flatpak/exports/share/applications"]
        for d in dirs:
            for f in sorted(glob.glob(d + "/*.desktop")):
                i = desktop_info(f)
                if i and i[0] not in seen and not os.path.basename(f).startswith("nd18e-"):
                    seen.add(i[0])
                    s.avail.append((i[0], f))
        s.avail.sort(key=lambda x: x[0].lower())
        for n, f in s.avail:
            s.avl.insert("end", n)

    def auto_add(s):
        sel = s.avl.curselection()
        if not sel:
            return
        name, f = s.avail[sel[0]]
        if not messagebox.askyesno("Autostart", "Uruchamiać %s automatycznie przy każdym logowaniu?" % name):
            return
        os.makedirs(AUTO, exist_ok=True)
        shutil.copy(f, os.path.join(AUTO, os.path.basename(f)))
        s.auto_refresh()

    def auto_remove(s):
        sel = s.aul.curselection()
        if sel:
            try:
                os.remove(s.auto_user[sel[0]])
            except Exception:
                pass
            s.auto_refresh()

    # ------------------------------------------------------------- tryb gry
    def page_game(s, p):
        s.title_lbl(p, "Tryb gry", "Po włączeniu wyłącza kompozytor (wszystkie animacje okien), blokuje wygaszanie "
                    "ekranu i przełącza procesor na pełną wydajność, żeby system skupił się na grze. "
                    "Po wylogowaniu lub restarcie tryb gry wyłącza się sam.")
        s.gb = tk.Button(p, command=s.toggle_game, relief="flat", bd=0, font=("sans", 14, "bold"), padx=30, pady=16)
        s.gb.pack(anchor="w", padx=20, pady=20)
        tk.Label(p, text="Tryb gry możesz też przełączyć z menu Start (Tryb gry).", bg=BG, fg=DIM).pack(
            anchor="w", padx=20)
        s.paint_game()

    def game_on(s):
        return sh("nd18e-gamemode status") == "on"

    def paint_game(s):
        on = s.game_on()
        s.gb.config(text="TRYB GRY: WŁĄCZONY" if on else "TRYB GRY: WYŁĄCZONY",
                    bg="#16a34a" if on else BTN, fg="white")

    def toggle_game(s):
        subprocess.run(["nd18e-gamemode", "off" if s.game_on() else "on"])
        s.paint_game()

    # ------------------------------------------------- motyw, pasek, tapeta
    def page_theme(s, p):
        s.title_lbl(p, "Motyw i tapeta", "Tryb ciemny (czarny) lub jasny, kolor paska zadań i własna tapeta.")
        tk.Label(p, text="Tryb:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(anchor="w", padx=20, pady=(12, 4))
        tf = tk.Frame(p, bg=BG)
        tf.pack(anchor="w", padx=20)
        s.thb = {}
        for key, name in (("dark", "Ciemny"), ("light", "Jasny")):
            b = tk.Button(tf, text=name, command=lambda k=key: s.set_theme(k), relief="flat", bd=0, padx=26, pady=8)
            b.pack(side="left", padx=(0, 6))
            s.thb[key] = b
        tk.Label(p, text="Kolor paska zadań:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(
            anchor="w", padx=20, pady=(16, 4))
        pf = tk.Frame(p, bg=BG)
        pf.pack(anchor="w", padx=20)
        for i, (name, hx) in enumerate(PANEL_COLORS):
            tk.Button(pf, text=name, command=lambda h=hx: s.set_panel(h), relief="flat", bd=0, padx=10, pady=8,
                      bg=hx or BTN, fg=("#000000" if hx and lum(hx) > 150 else "#ffffff"), width=18).grid(
                row=i // 4, column=i % 4, padx=3, pady=3, sticky="ew")
        btn(pf, "Własny kolor...", s.custom_panel).grid(row=2, column=0, padx=3, pady=3, sticky="ew")
        tk.Label(p, text="Tapeta pulpitu:", bg=BG, fg=FG, font=("sans", 11, "bold")).pack(
            anchor="w", padx=20, pady=(16, 4))
        s.wmode = tk.StringVar(value="zoom")
        wf = tk.Frame(p, bg=BG)
        wf.pack(anchor="w", padx=20)
        for v, t in (("zoom", "Wypełnij"), ("fit", "Dopasuj"), ("stretch", "Rozciągnij"), ("center", "Wyśrodkuj")):
            tk.Radiobutton(wf, text=t, variable=s.wmode, value=v, bg=BG, fg=FG, selectcolor=PANEL,
                           activebackground=BG, activeforeground=FG, highlightthickness=0).pack(side="left", padx=(0, 10))
        bf = tk.Frame(p, bg=BG)
        bf.pack(anchor="w", padx=20, pady=8)
        btn(bf, "Wybierz plik...", s.pick_wall, red=True).pack(side="left")
        btn(bf, "Przywróć domyślną", lambda: s.set_wall(DEFAULT_WALL)).pack(side="left", padx=8)
        s.th_msg = tk.Label(p, text="Panel i aplikacje LXQt zmieniają wygląd od razu, część programów po ponownym uruchomieniu.", bg=BG, fg=DIM, wraplength=800, justify="left")
        s.th_msg.pack(anchor="w", padx=20, pady=4)
        s.paint_theme()

    def paint_theme(s):
        cur = cfg_get(LXQT_CONF, "General", "theme", "dark")
        for k, b in s.thb.items():
            b.config(bg=RED if k == cur else BTN, fg="white" if k == cur else FG)

    def set_theme(s, k):
        cfg_set(LXQT_CONF, "General", "theme", k)
        cfg_set(GTK_CONF, "Settings", "gtk-application-prefer-dark-theme", "true" if k == "dark" else "false")
        # to okno i pozostale programy ND18E czytaja tryb przy starcie - otwieramy je ponownie na zakladce Motyw
        subprocess.Popen([sys.executable, os.path.abspath(sys.argv[0]), "--tab=%d" % TAB_THEME])
        s.destroy()

    def set_panel(s, hx):
        if hx is None:
            for key in ("background-color", "font-color", "opacity"):
                cfg_set(PANEL_CONF, "panel1", key, None)
        else:
            cfg_set(PANEL_CONF, "panel1", "background-color", hx)
            cfg_set(PANEL_CONF, "panel1", "font-color", "#000000" if lum(hx) > 150 else "#ffffff")
            cfg_set(PANEL_CONF, "panel1", "opacity", "100")
        subprocess.Popen("pkill -x lxqt-panel; sleep 2; pgrep -x lxqt-panel >/dev/null || "
                         "(nohup lxqt-panel >/dev/null 2>&1 &)", shell=True)
        s.th_msg.config(text="Zapisano - panel odświeży się za chwilę.")

    def custom_panel(s):
        c = colorchooser.askcolor(title="Kolor paska zadań")[1]
        if c:
            s.set_panel(c)

    def pick_wall(s):
        f = filedialog.askopenfilename(title="Wybierz tapetę", initialdir=os.path.expanduser("~"),
                                       filetypes=[("Obrazy", "*.png *.jpg *.jpeg *.webp *.bmp"), ("Wszystkie", "*.*")])
        if f:
            s.set_wall(f)

    def set_wall(s, path):
        dst = path
        if not path.startswith("/usr/share/"):
            try:
                os.makedirs(WALL_DIR, exist_ok=True)
                dst = os.path.join(WALL_DIR, os.path.basename(path))
                if os.path.abspath(path) != os.path.abspath(dst):
                    shutil.copy(path, dst)
            except Exception as e:
                messagebox.showerror("Tapeta", "Nie można użyć tego pliku:\n%s" % e)
                return
        subprocess.Popen(["pcmanfm-qt", "--profile=lxqt", "--set-wallpaper=" + dst, "--wallpaper-mode=" + s.wmode.get()])
        cfg_set(PCMAN_CONF, "Desktop", "Wallpaper", dst)
        cfg_set(PCMAN_CONF, "Desktop", "WallpaperMode", s.wmode.get())
        s.th_msg.config(text="Tapeta ustawiona: %s" % os.path.basename(dst))

    # ---------------------------------------------------------------- system
    def run_root(s, payload):
        if not payload:
            return True
        try:
            r = subprocess.run(["pkexec", ROOT], input=json.dumps(payload), text=True, capture_output=True,
                               timeout=180)
            return r.returncode == 0
        except Exception:
            return False

    def lang_payload(s):
        l = LANGS[s.lang_idx]
        return {"locale": l[1], "kbd": l[2]}

    def pin_payload(s):
        m = s.pin_mode.get()
        if m == "set":
            return {"pin": s.pin1.get()}
        if m == "remove":
            return {"pin": "remove"}
        return {}

    def apply_lang(s):
        ok = s.run_root(s.lang_payload())
        messagebox.showinfo("Język", "Zapisano. Zmiana będzie widoczna po ponownym zalogowaniu." if ok
                            else "Nie udało się zapisać zmian (anulowano lub błąd).")

    def apply_pin(s):
        if s.pin_mode.get() == "skip" or not s.pin_ok():
            return
        ok = s.run_root(s.pin_payload())
        messagebox.showinfo("PIN", "Zapisano." if ok else "Nie udało się zapisać zmian (anulowano lub błąd).")

    # ---------------------------------------------------------------- tryby
    def build_settings(s):
        nb = ttk.Notebook(s)
        nb.pack(fill="both", expand=True)
        for name, fn, kw in (("Język", s.page_lang, {"apply_btn": True}), ("Czas", s.page_time, {}),
                             ("Ekran", s.page_screen, {}), ("PIN", s.page_pin, {"apply_btn": True}),
                             ("Motyw", s.page_theme, {}), ("Animacje", s.page_look, {}),
                             ("Autostart", s.page_auto, {}), ("Tryb gry", s.page_game, {}),
                             ("Sprzęt", s.page_hw, {})):
            f = tk.Frame(nb, bg=BG)
            nb.add(f, text=name)
            fn(f, **kw)
        if 0 <= START_TAB < nb.index("end"):
            nb.select(START_TAB)

    def build_wizard(s):
        s.step = 0
        s.hdr = tk.Frame(s, bg=BG)
        s.hdr.pack(fill="x")
        s.nlbl = tk.Label(s.hdr, text="N", bg=BG, fg=RED, font=("sans", 40, "bold"))
        s.nlbl.pack(side="left", padx=(20, 10))
        tk.Label(s.hdr, text="Dziękujemy za wybranie systemu ND18E Linux", bg=BG, fg=FG,
                 font=("sans", 14, "bold")).pack(side="left")
        s.body = tk.Frame(s, bg=BG)
        s.body.pack(fill="both", expand=True)
        s.nav = tk.Frame(s, bg=BG)
        s.nav.pack(fill="x", padx=20, pady=12)
        s.back = btn(s.nav, "Wstecz", lambda: s.go(-1))
        s.back.pack(side="left")
        s.cnt = tk.Label(s.nav, bg=BG, fg=DIM)
        s.cnt.pack(side="left", expand=True)
        s.next = btn(s.nav, "Dalej", lambda: s.go(1), red=True, padx=26)
        s.next.pack(side="right")
        s.pages = []
        for fn in (s.page_lang, s.page_pin, s.page_look, s.page_hw, s.page_done):
            f = tk.Frame(s.body, bg=BG)
            fn(f)
            s.pages.append(f)
        s.show_step()
        s.pulse(0)

    def page_done(s, p):
        s.title_lbl(p, "Wszystko gotowe", "Aplikacje instalujesz sam ze Sklepu - system jest czysty i lekki. "
                    "Ustawienia zmienisz później w menu: Konfiguracja systemu.\n\n"
                    "Skróty: Super = menu Start,  Print = zrzut ekranu,  Ctrl+Print = zrzut obszaru,  Alt+Print = zrzut okna.")
        btn(p, "Otwórz Sklep z aplikacjami", lambda: subprocess.Popen(["nd18e-store"])).pack(
            anchor="w", padx=20, pady=16)

    def pulse(s, t):
        import math
        a = 0.5 + 0.5 * math.sin(t / 8.0)
        r = int(0x7a + (0xff - 0x7a) * a)
        s.nlbl.config(fg="#%02x%02x%02x" % (r, 0x14, 0x24))
        s.after(40, s.pulse, t + 1)

    def show_step(s):
        for i, f in enumerate(s.pages):
            if i == s.step:
                f.pack(fill="both", expand=True)
            else:
                f.pack_forget()
        s.cnt.config(text="Krok %d z %d" % (s.step + 1, len(s.pages)))
        s.back.config(state="normal" if s.step else "disabled")
        s.next.config(text="Zakończ" if s.step == len(s.pages) - 1 else "Dalej")

    def go(s, d):
        if d > 0:
            if s.step == 1 and not s.pin_ok():
                return
            if s.step == len(s.pages) - 1:
                return s.finish()
        s.step = max(0, min(len(s.pages) - 1, s.step + d))
        s.show_step()

    def finish(s):
        payload = s.lang_payload()
        payload.update(s.pin_payload())
        if not s.run_root(payload):
            messagebox.showwarning("ND18E", "Nie zapisano języka/PIN-u (anulowano lub błąd).\n"
                                   "Możesz je ustawić później w: Konfiguracja systemu.")
        os.makedirs(os.path.dirname(MARK), exist_ok=True)
        open(MARK, "w").close()
        s.destroy()


App().mainloop()
