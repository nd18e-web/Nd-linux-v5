#!/usr/bin/env python3
# ND18E - pomocnik z uprawnieniami roota (uruchamiany przez pkexec z Konfiguracji).
# Odczytuje JSON ze stdin: {"locale": "pl_PL.UTF-8", "kbd": "pl", "pin": "1234" | "remove"}
# Zmienia TYLKO: jezyk systemu, uklad klawiatury, strefe czasowa, automatyczna godzine i haslo/PIN uzytkownika, ktory uruchomil pkexec.
import json
import os
import pwd
import re
import subprocess
import sys


def set_locale(loc):
    if not re.fullmatch(r"[a-z]{2,3}_[A-Z]{2}\.UTF-8", loc):
        raise ValueError("zly locale")
    lines = open("/etc/locale.gen", encoding="utf-8").read().splitlines()
    found = False
    for i, l in enumerate(lines):
        if re.fullmatch(r"#\s*" + re.escape(loc) + r" UTF-8", l.strip()):
            lines[i] = loc + " UTF-8"
            found = True
        elif l.strip() == loc + " UTF-8":
            found = True
    if not found:
        raise ValueError("brak locale w /etc/locale.gen")
    open("/etc/locale.gen", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    subprocess.run(["locale-gen"], check=True, capture_output=True)
    subprocess.run(["update-locale", "LANG=" + loc], check=True)


def set_kbd(kbd):
    if not re.fullmatch(r"[a-z]{2,3}", kbd):
        raise ValueError("zly uklad")
    open("/etc/default/keyboard", "w").write(
        'XKBMODEL="pc105"\nXKBLAYOUT="%s"\nXKBVARIANT=""\nXKBOPTIONS="grp:alt_shift_toggle"\nBACKSPACE="guess"\n' % kbd)
    os.makedirs("/etc/X11/xorg.conf.d", exist_ok=True)
    open("/etc/X11/xorg.conf.d/00-keyboard.conf", "w").write(
        'Section "InputClass"\n    Identifier "ND18E keyboard"\n    MatchIsKeyboard "on"\n'
        '    Option "XkbLayout" "%s"\n    Option "XkbModel" "pc105"\nEndSection\n' % kbd)


def set_pin(user, pin):
    if pin == "remove":
        subprocess.run(["passwd", "-d", user], check=True, capture_output=True)
        return
    if not re.fullmatch(r"\d{4,8}", pin):
        raise ValueError("PIN: 4-8 cyfr")
    subprocess.run(["chpasswd"], input="%s:%s\n" % (user, pin), text=True, check=True, capture_output=True)


def set_tz(tz):
    if not re.fullmatch(r"[A-Za-z0-9_+\-]+(/[A-Za-z0-9_+\-]+){0,2}", tz) or not os.path.isfile("/usr/share/zoneinfo/" + tz):
        raise ValueError("zla strefa czasowa")
    subprocess.run(["timedatectl", "set-timezone", tz], check=True, capture_output=True)


def set_ntp(on):
    subprocess.run(["timedatectl", "set-ntp", "true" if on else "false"], check=True, capture_output=True)


def main():
    if os.geteuid() != 0:
        sys.exit("wymaga roota (uruchom przez pkexec)")
    user = pwd.getpwuid(int(os.environ.get("PKEXEC_UID", "-1"))).pw_name
    data = json.load(sys.stdin)
    if data.get("locale"):
        set_locale(data["locale"])
    if data.get("kbd"):
        set_kbd(data["kbd"])
    if data.get("timezone"):
        set_tz(data["timezone"])
    if "ntp" in data:
        set_ntp(bool(data["ntp"]))
    if data.get("pin"):
        set_pin(user, data["pin"])


try:
    main()
except Exception as e:
    sys.exit("blad: %s" % e)
