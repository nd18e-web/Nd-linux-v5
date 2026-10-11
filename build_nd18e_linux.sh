#!/bin/bash
# ND18E Linux - czysty, lekki system: pulpit LXQt (pasek + wlasne menu Start z ikona "N": wyszukiwarka, boczna ramka, Wylacz), intro "N" przy starcie,
# Konfiguracja systemu (motyw ciemny/jasny, kolor paska, tapeta; GTX 1050 Ti + i5-7400), Menedzer zadan, Menedzer plikow (PCManFM-Qt), Sklep z aplikacjami (Flathub), dzwieki i animacje.
# Nic wiecej nie jest zainstalowane - aplikacje instalujesz sam ze Sklepu.
# Wymagania: system do budowania ISO: Debian 12 (najlepiej) albo Ubuntu 24.04 (starsze Ubuntu nie znaja kluczy Debiana 12 i buduja z bledem).
# Np. VirtualBox: 8 GB RAM, 40 GB wolnego dysku, internet. Budowanie trwa 20-60 min, pobiera ok. 2 GB.
# Gdy chcesz, zeby instalator pokazywal strony Jezyk/Klawiatura/Strefa czasowa, ustaw nizej SKIP_INSTALLER_LANG_PAGES=0.
# Obok skryptu musza lezec: nd18e-taskmgr.py, nd18e-store.py, nd18e-setup.py, nd18e-root.py, nd18e-start.py, nd18e-make-assets.py
# Uzycie: chmod +x build_nd18e_linux.sh && ./build_nd18e_linux.sh   -> ND18E_Linux.iso
set -e
SKIP_INSTALLER_LANG_PAGES=1   # 1 = instalator bez wyboru jezyka/klawiatury/strefy (to ustawiasz pozniej w Konfiguracji systemu)
for f in nd18e-taskmgr.py nd18e-store.py nd18e-setup.py nd18e-root.py nd18e-start.py nd18e-make-assets.py; do
  [ -f "$f" ] || { echo "Brak pliku $f obok skryptu"; exit 1; }
done
sudo apt-get update
sudo apt-get install -y live-build sox wget debootstrap python3-pil debian-archive-keyring

sudo rm -rf nd18e_build && mkdir nd18e_build && cd nd18e_build

lb config --distribution bookworm --architectures amd64 \
  --archive-areas "main contrib non-free non-free-firmware" \
  --apt-recommends false \
  --debian-installer none --binary-images iso-hybrid \
  --iso-application "ND18E Linux" --iso-volume ND18E --memtest none \
  --bootappend-live "boot=live components quiet splash locales=pl_PL.UTF-8 keyboard-layouts=pl timezone=Europe/Warsaw"

C=config/includes.chroot
mkdir -p config/package-lists config/hooks/normal $C/etc/skel/Desktop $C/etc/skel/.config/lxqt \
  $C/etc/skel/.config/pcmanfm-qt/lxqt $C/etc/xdg/autostart $C/usr/share/sounds/nd18e \
  $C/usr/share/plymouth/themes/nd18e $C/usr/share/backgrounds $C/usr/local/bin $C/usr/share/applications $C/usr/share/icons/nd18e

# ---------- Pakiety: tylko podstawa systemu ----------
cat > config/package-lists/nd18e.list.chroot <<'EOF'
# --- pulpit ---
lxqt-core lxqt-config lxqt-policykit lxqt-themes lightdm lightdm-gtk-greeter openbox picom
pcmanfm-qt lxqt-archiver zip unzip p7zip-full scrot xclip xbindkeys libnotify-bin qterminal libqt5svg5 adwaita-icon-theme xdg-utils xdg-user-dirs x11-xserver-utils gamemode systemd-timesyncd
# --- serwer grafiki + sterowniki MYSZY, KLAWIATURY, TOUCHPADA ---
xserver-xorg-core xserver-xorg-input-libinput xserver-xorg-video-vesa
xkb-data x11-xkb-utils keyboard-configuration console-setup locales
# --- sesja, uprawnienia, dyski ---
libpam-systemd dbus-user-session dbus-x11 policykit-1 udisks2 gvfs
# --- DZWIEK (PipeWire + ALSA + firmware) ---
pipewire-audio pipewire-pulse wireplumber pulseaudio-utils alsa-utils alsa-ucm-conf firmware-sof-signed
# --- INTERNET (kabel + Wi-Fi) ---
network-manager network-manager-gnome wpasupplicant wireless-regdb iw rfkill ca-certificates
firmware-linux firmware-misc-nonfree firmware-realtek firmware-iwlwifi firmware-atheros firmware-brcm80211
# --- narzedzia ND18E ---
python3 python3-tk python3-psutil pciutils
flatpak xdg-desktop-portal-gtk
# --- grafika / NVIDIA (dkms) ---
mesa-vulkan-drivers libgl1-mesa-dri linux-headers-amd64 dkms gcc make
fonts-noto fonts-noto-cjk fonts-dejavu plymouth plymouth-themes calamares calamares-settings-debian sudo
# --- instalator: narzedzia dyskow i bootloader (BIOS + UEFI) ---
grub-efi-amd64 grub-efi-amd64-signed shim-signed grub-pc-bin efibootmgr os-prober rsync parted dosfstools e2fsprogs ntfs-3g
EOF

# ---------- Klawiatura (PL) i mysz/touchpad (libinput) ----------
mkdir -p $C/etc/X11/xorg.conf.d $C/etc/default
cat > $C/etc/default/keyboard <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="pl"
XKBVARIANT=""
XKBOPTIONS="grp:alt_shift_toggle"
BACKSPACE="guess"
EOF
echo 'LANG=pl_PL.UTF-8' > $C/etc/default/locale
cat > $C/etc/X11/xorg.conf.d/00-keyboard.conf <<'EOF'
Section "InputClass"
    Identifier "ND18E keyboard"
    MatchIsKeyboard "on"
    Option "XkbLayout" "pl"
    Option "XkbModel" "pc105"
EndSection
EOF
cat > $C/etc/X11/xorg.conf.d/40-libinput.conf <<'EOF'
Section "InputClass"
    Identifier "ND18E mouse"
    MatchIsPointer "on"
    MatchDriver "libinput"
    Option "AccelProfile" "adaptive"
EndSection
Section "InputClass"
    Identifier "ND18E touchpad"
    MatchIsTouchpad "on"
    MatchDriver "libinput"
    Option "Tapping" "on"
    Option "NaturalScrolling" "false"
    Option "DisableWhileTyping" "on"
EndSection
EOF

# ---------- Programy ND18E ----------
for a in taskmgr store setup root start; do cp ../nd18e-$a.py $C/usr/local/bin/nd18e-$a; chmod 755 $C/usr/local/bin/nd18e-$a; done
mk() { # nazwa, polecenie, ikona
  cat > $C/usr/share/applications/$1.desktop <<EOF
[Desktop Entry]
Type=Application
Name=$2
Exec=$3
Icon=$4
Categories=System;
EOF
  cp $C/usr/share/applications/$1.desktop $C/etc/skel/Desktop/
}
mk nd18e-taskmgr "Menedzer zadan" nd18e-taskmgr utilities-system-monitor
mk nd18e-store "Sklep z aplikacjami" nd18e-store system-software-install
mk nd18e-setup "Konfiguracja systemu" nd18e-setup preferences-system
cat > $C/usr/share/applications/nd18e-start.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Menu Start
Exec=nd18e-start
Icon=/usr/share/icons/nd18e/n.svg
Categories=System;
EOF
cat > $C/usr/share/applications/nd18e-shot.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Zrzut ekranu (zaznacz obszar)
Exec=nd18e-shot area
Icon=camera-photo
Categories=Utility;
EOF
cat > $C/etc/xdg/autostart/nd18e-setup.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E Konfiguracja (pierwsze uruchomienie)
Exec=nd18e-setup --first-run
NoDisplay=true
EOF

# ---------- Ikona "N" (menu Start) ----------
cat > $C/usr/share/icons/nd18e/n.svg <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect x="2" y="2" width="60" height="60" rx="14" fill="#0a0506" stroke="#e11d2e" stroke-width="3"/>
<path d="M19 47 V17 L45 47 V17" fill="none" stroke="#e11d2e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
EOF

# ---------- Dzwieki ----------
S=$C/usr/share/sounds/nd18e
sox -n -r 44100 -c 2 /tmp/n1.wav synth 0.35 sine 392 fade h 0.02 0.35 0.25 vol 0.5
sox -n -r 44100 -c 2 /tmp/n2.wav synth 0.35 sine 494 fade h 0.02 0.35 0.25 vol 0.5
sox -n -r 44100 -c 2 /tmp/n3.wav synth 1.2 sine 587 sine 784 fade h 0.02 1.2 1.0 vol 0.45
sox /tmp/n1.wav /tmp/n2.wav /tmp/n3.wav $S/startup.wav reverb
sox -n -r 44100 -c 2 /tmp/d1.wav synth 0.12 sine 880 fade h 0.01 0.12 0.08 vol 0.5
sox -n -r 44100 -c 2 /tmp/d2.wav synth 0.25 sine 1175 fade h 0.01 0.25 0.2 vol 0.5
sox /tmp/d1.wav /tmp/d2.wav $S/done.wav
mk2() { # nazwa, czestotliwosc 1, czestotliwosc 2
  sox -n -r 44100 -c 2 /tmp/a.wav synth 0.10 sine $2 fade h 0.01 0.10 0.07 vol 0.45
  sox -n -r 44100 -c 2 /tmp/b.wav synth 0.16 sine $3 fade h 0.01 0.16 0.12 vol 0.45
  sox /tmp/a.wav /tmp/b.wav $S/$1.wav
}
sox -n -r 44100 -c 2 $S/shot.wav synth 0.12 pinknoise fade h 0.005 0.12 0.1 vol 0.5
mk2 connect 660 990      # podlaczono urzadzenie (USB)
mk2 disconnect 990 660   # odlaczono urzadzenie
mk2 net-up 523 784       # internet polaczony
mk2 net-down 392 262     # internet rozlaczony
cat > $C/usr/local/bin/nd18e-shot <<'EOF'
#!/bin/bash
# ND18E zrzuty ekranu: full (caly ekran) | area (zaznacz obszar) | window (aktywne okno)
# Zapis do Obrazy/Zrzuty ekranu + kopia do schowka + powiadomienie i dzwiek.
D="$(xdg-user-dir PICTURES 2>/dev/null)"
{ [ -n "$D" ] && [ "$D" != "$HOME" ]; } || D="$HOME/Pictures"
D="$D/Zrzuty ekranu"; mkdir -p "$D"
F="$D/Zrzut_$(date +%Y-%m-%d_%H-%M-%S).png"
case "$1" in
  area) sleep 0.3; scrot -s "$F" ;;
  window) scrot -u "$F" ;;
  *) scrot "$F" ;;
esac
[ -s "$F" ] || exit 0
xclip -selection clipboard -t image/png -i "$F" 2>/dev/null
[ -e "$HOME/.config/nd18e-sounds-off" ] || paplay /usr/share/sounds/nd18e/shot.wav 2>/dev/null &
notify-send -i camera-photo "Zrzut ekranu" "Zapisano: $F (skopiowano też do schowka)" 2>/dev/null
exit 0
EOF
chmod +x $C/usr/local/bin/nd18e-shot
cat > $C/etc/skel/.xbindkeysrc <<'EOF'
"nd18e-shot full"
    Print
"nd18e-shot area"
    Control + Print
"nd18e-shot window"
    Alt + Print
"nd18e-start"
    Super_L
EOF
cat > $C/etc/xdg/autostart/nd18e-keys.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E skroty klawiszowe
Exec=xbindkeys
NoDisplay=true
EOF
cat > $C/usr/local/bin/nd18e-sounds <<'EOF'
#!/bin/bash
# ND18E - dzwieki systemowe: USB podlaczone/odlaczone, internet polaczony/rozlaczony
D=/usr/share/sounds/nd18e
OFF="$HOME/.config/nd18e-sounds-off"
play() { [ -e "$OFF" ] || paplay "$D/$1.wav" 2>/dev/null & }
sleep 3
[ -e "$OFF" ] || paplay "$D/startup.wav" 2>/dev/null &   # dzwiek startu
sleep 3   # urzadzenia podlaczone przy starcie nie graja
udevadm monitor --udev --subsystem-match=usb --property 2>/dev/null | while read -r l; do
  case "$l" in
    ACTION=add) a=add ;;
    ACTION=remove) a=remove ;;
    DEVTYPE=usb_device) [ "$a" = add ] && play connect; [ "$a" = remove ] && play disconnect ;;
    "") a= ;;
  esac
done &
LC_ALL=C nmcli monitor 2>/dev/null | while read -r l; do
  case "$l" in
    *": disconnected"*) play net-down ;;
    *": connected"*) play net-up ;;
  esac
done &
wait
EOF
chmod +x $C/usr/local/bin/nd18e-sounds
cat > $C/etc/xdg/autostart/nd18e-sounds.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E dzwieki systemowe
Exec=nd18e-sounds
NoDisplay=true
EOF

# ---------- Tapeta + intro przy starcie: samo "N" na czarnym tle, pulsuje (Plymouth) ----------
P=$C/usr/share/plymouth/themes/nd18e
python3 ../nd18e-make-assets.py $C/usr/share/backgrounds/nd18e.png $P
cat > $P/nd18e.plymouth <<'EOF'
[Plymouth Theme]
Name=ND18E
Description=ND18E Linux
ModuleName=script
[script]
ImageDir=/usr/share/plymouth/themes/nd18e
ScriptFile=/usr/share/plymouth/themes/nd18e/nd18e.script
EOF
cat > $P/nd18e.script <<'EOF'
Window.SetBackgroundTopColor(0, 0, 0);
Window.SetBackgroundBottomColor(0, 0, 0);
k = Window.GetHeight() / 1080;
if (k > 1) k = 1;
n = Image("n.png");
g = Image("glow.png");
n = n.Scale(n.GetWidth() * k, n.GetHeight() * k);
g = g.Scale(g.GetWidth() * k, g.GetHeight() * k);
sn = Sprite(n);
sg = Sprite(g);
sn.SetZ(10);
sg.SetZ(5);
sn.SetX(Window.GetWidth() / 2 - n.GetWidth() / 2);
sn.SetY(Window.GetHeight() / 2 - n.GetHeight() / 2);
sg.SetX(Window.GetWidth() / 2 - g.GetWidth() / 2);
sg.SetY(Window.GetHeight() / 2 - g.GetHeight() / 2);
t = 0;
fun refresh() {
  t++;
  a = 0.5 + 0.5 * Math.Sin(t / 16);
  sg.SetOpacity(0.10 + 0.90 * a);
  sn.SetOpacity(0.80 + 0.20 * a);
}
Plymouth.SetRefreshFunction(refresh);
EOF

# Ekran logowania z ta sama tapeta; sesja LXQt wybrana jawnie (zeby nie trafic w samego Openboxa bez paska)
mkdir -p $C/etc/lightdm/lightdm.conf.d
cat > $C/etc/lightdm/lightdm.conf.d/50-nd18e.conf <<'EOF'
[Seat:*]
greeter-session=lightdm-gtk-greeter
user-session=lxqt
autologin-session=lxqt
EOF
cat > $C/etc/lightdm/lightdm-gtk-greeter.conf <<'EOF'
[greeter]
background=/usr/share/backgrounds/nd18e.png
user-background=false
EOF

# ---------- Uprawnienia: Konfiguracja systemu zmienia jezyk/PIN/czas bez pytania o haslo ----------
mkdir -p $C/usr/share/polkit-1/actions
cat > $C/usr/share/polkit-1/actions/pl.nd18e.root.policy <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN" "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>
  <action id="pl.nd18e.root">
    <description>Zmiana ustawien systemu ND18E</description>
    <message>Zmiana ustawien systemu ND18E</message>
    <defaults>
      <allow_any>no</allow_any>
      <allow_inactive>no</allow_inactive>
      <allow_active>yes</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/local/bin/nd18e-root</annotate>
  </action>
</policyconfig>
EOF

# ---------- Instalator: grafiki "N" i marker (strony jezyka/klawiatury pomijane) ----------
mkdir -p $C/etc
[ "$SKIP_INSTALLER_LANG_PAGES" = 1 ] && touch $C/etc/nd18e-skip-pages
cat > $C/etc/nd18e-show.qml <<'EOF'
import QtQuick 2.0
Rectangle {
    color: "#0a0a0a"
    Text {
        anchors.centerIn: parent
        text: "N"
        color: "#e11d2e"
        font.pixelSize: 180
        font.bold: true
    }
}
EOF

# ---------- Tryb gry, zapisane ustawienia ekranu/tekstu ----------
cat > $C/usr/local/bin/nd18e-gamemode <<'EOF'
#!/bin/bash
# ND18E tryb gry: on | off | toggle | status
# Wlaczony: bez kompozytora (zero animacji okien), bez wygaszania ekranu, procesor na pelnej wydajnosci (GameMode).
# Stan trzymany w katalogu tymczasowym sesji - po wylogowaniu/restarcie tryb gry sam sie wylacza.
R="${XDG_RUNTIME_DIR:-/tmp}"
S="$R/nd18e-gamemode"; P="$R/nd18e-gamemode.pid"
anim=$(cat "$HOME/.config/nd18e-anim" 2>/dev/null || echo light)
case "$1" in
  on)
    [ -e "$S" ] && exit 0
    pkill -x picom
    xset s off -dpms 2>/dev/null
    nohup gamemoderun sleep infinity >/dev/null 2>&1 &
    echo $! > "$P"; touch "$S" ;;
  off)
    [ -e "$S" ] || exit 0
    [ -f "$P" ] && kill "$(cat "$P")" 2>/dev/null
    rm -f "$S" "$P"
    xset s on +dpms 2>/dev/null
    [ "$anim" = off ] || { picom -b || picom -b --backend xrender; } ;;
  toggle) if [ -e "$S" ]; then exec "$0" off; else exec "$0" on; fi ;;
  status) [ -e "$S" ] && echo on || echo off ;;
esac
EOF
cat > $C/usr/local/bin/nd18e-prefs <<'EOF'
#!/bin/bash
# Stosuje zapisane ustawienia ekranu i wielkosci tekstu przy logowaniu.
D="$HOME/.config/nd18e-display"; X="$HOME/.config/nd18e-dpi"
if [ -f "$D" ]; then read -r out mode < "$D"; [ -n "$out" ] && [ -n "$mode" ] && xrandr --output "$out" --mode "$mode"; fi
if [ -f "$X" ]; then echo "Xft.dpi: $(tr -dc 0-9 < "$X")" | xrdb -merge; fi
EOF
chmod 755 $C/usr/local/bin/nd18e-gamemode $C/usr/local/bin/nd18e-prefs
cat > $C/etc/xdg/autostart/nd18e-prefs.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E ustawienia ekranu
Exec=nd18e-prefs
NoDisplay=true
EOF
cat > $C/usr/share/applications/nd18e-gamemode.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Tryb gry
Exec=nd18e-gamemode toggle
Icon=applications-games
Categories=System;Game;
EOF

# ---------- Wyglad i animacje: ciemny motyw, panel z ikona N, kompozytor (cienie, zanikanie okien) ----------
cat > $C/etc/skel/.config/lxqt/lxqt.conf <<'EOF'
[General]
theme=dark
[Qt]
style=Fusion
EOF
cat > $C/etc/skel/.config/lxqt/panel.conf <<'EOF'
[General]
__userfile__=true
[panel1]
alignment=-1
desktop=0
iconSize=26
panelSize=44
position=Bottom
background-color=#a3121e
font-color=#ffffff
opacity=100
plugins=quicklaunch, taskbar, tray, volume, worldclock
[quicklaunch]
alignment=Left
type=quicklaunch
apps\size=1
apps\1\desktop=/usr/share/applications/nd18e-start.desktop
[taskbar]
alignment=Left
type=taskbar
[tray]
alignment=Right
type=tray
[volume]
alignment=Right
type=volume
audioEngine=PulseAudio
[worldclock]
alignment=Right
type=worldclock
EOF
cat > $C/etc/skel/.config/pcmanfm-qt/lxqt/settings.conf <<'EOF'
[Desktop]
Wallpaper=/usr/share/backgrounds/nd18e.png
WallpaperMode=stretch
EOF
# --- Animacje: trzy poziomy (wylaczone / lekkie / pelne), przelaczane w Konfiguracji ---
mkdir -p $C/etc/xdg/nd18e $C/etc/skel/.config/picom
cat > $C/etc/xdg/nd18e/picom-off.conf <<'EOF'
backend = "glx";
vsync = true;
shadow = false;
fading = false;
unredir-if-possible = true;
EOF
cat > $C/etc/xdg/nd18e/picom-light.conf <<'EOF'
backend = "glx";
vsync = true;
use-damage = true;
unredir-if-possible = true;
shadow = true;
shadow-radius = 16;
shadow-opacity = 0.38;
shadow-offset-x = -10;
shadow-offset-y = -8;
shadow-exclude = [ "window_type = 'dock'", "window_type = 'desktop'", "_GTK_FRAME_EXTENTS@:c" ];
fading = true;
fade-in-step = 0.045;
fade-out-step = 0.055;
fade-delta = 7;
corner-radius = 10;
rounded-corners-exclude = [ "window_type = 'dock'", "window_type = 'desktop'" ];
inactive-dim = 0.04;
focus-exclude = [ "window_type = 'dock'", "window_type = 'popup_menu'" ];
wintypes:
{
  popup_menu = { opacity = 0.97; };
  dropdown_menu = { opacity = 0.97; };
  dock = { shadow = false; };
};
EOF
cat > $C/etc/xdg/nd18e/picom-full.conf <<'EOF'
backend = "glx";
vsync = true;
use-damage = true;
unredir-if-possible = true;
shadow = true;
shadow-radius = 18;
shadow-opacity = 0.6;
shadow-offset-x = -14;
shadow-offset-y = -12;
shadow-exclude = [ "window_type = 'dock'", "window_type = 'desktop'", "_GTK_FRAME_EXTENTS@:c" ];
fading = true;
fade-in-step = 0.035;
fade-out-step = 0.045;
fade-delta = 8;
corner-radius = 12;
rounded-corners-exclude = [ "window_type = 'dock'", "window_type = 'desktop'" ];
blur-method = "dual_kawase";
blur-strength = 5;
blur-background-exclude = [ "window_type = 'desktop'", "_GTK_FRAME_EXTENTS@:c" ];
inactive-dim = 0.12;
focus-exclude = [ "window_type = 'dock'" ];
opacity-rule = [ "92:class_g = 'qterminal'", "94:class_g = 'pcmanfm-qt'" ];
wintypes:
{
  tooltip = { fade = true; shadow = true; opacity = 0.92; };
  popup_menu = { opacity = 0.96; };
  dropdown_menu = { opacity = 0.96; };
  dock = { shadow = false; };
};
EOF
cp $C/etc/xdg/nd18e/picom-light.conf $C/etc/skel/.config/picom/picom.conf
cat > $C/etc/xdg/autostart/nd18e-picom.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=ND18E compositor
Exec=sh -c 'picom || picom --backend xrender'
NoDisplay=true
EOF
cat > $C/etc/skel/Desktop/install.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Zainstaluj ND18E Linux
Exec=sudo calamares
Icon=system-software-install
EOF
chmod +x $C/etc/skel/Desktop/*.desktop

# ---------- Hook: sterowniki (GTX 1050 Ti, i5-7400), Flathub, odchudzanie ----------
cat > config/hooks/normal/0100-nd18e.hook.chroot <<'EOF'
#!/bin/bash
# pliki z includes.chroot maja wlasciciela z hosta - programy uruchamiane jako root musza nalezec do roota
chown -R root:root /usr/local /etc/skel /etc/xdg /etc/lightdm /etc/X11/xorg.conf.d /usr/share/applications /usr/share/icons/nd18e /usr/share/sounds/nd18e /usr/share/polkit-1/actions 2>/dev/null || true
chown root:root /etc/default/keyboard /etc/default/locale /etc/nd18e-show.qml /usr/share/backgrounds/nd18e.png 2>/dev/null || true
chown -R root:root /usr/share/plymouth/themes/nd18e
ln -sf /usr/share/zoneinfo/Europe/Warsaw /etc/localtime; echo Europe/Warsaw > /etc/timezone
plymouth-set-default-theme nd18e || true
sed -i 's/^PRETTY_NAME=.*/PRETTY_NAME="ND18E Linux"/;s/^NAME=.*/NAME="ND18E Linux"/' /etc/os-release
# Instalator Calamares: nazwa "ND18E Linux", logo "N", kolory, bez slajdow Debiana
for f in /etc/calamares/branding/*/branding.desc /usr/share/calamares/branding/*/branding.desc; do
  [ -f "$f" ] || continue
  d="$(dirname "$f")"
  cp /usr/share/plymouth/themes/nd18e/logo.png "$d/nd18e-logo.png"
  cp /etc/nd18e-show.qml "$d/nd18e-show.qml"
  sed -i -E '/^\s*(productName|shortProductName|bootloaderEntryName):/s/Debian( GNU\/Linux)?/ND18E Linux/' "$f"
  sed -i -E 's/^(\s*(productLogo|productIcon|productWelcome):).*/\1 "nd18e-logo.png"/; s/^(\s*slideshow:).*/\1 "nd18e-show.qml"/' "$f"
  sed -i -E 's/^(\s*sidebarBackground:).*/\1 "#0a0a0a"/; s/^(\s*sidebarText:).*/\1 "#f2f2f2"/; s/^(\s*sidebarTextSelect:).*/\1 "#ffffff"/; s/^(\s*sidebarTextHighlight:).*/\1 "#e11d2e"/' "$f"
done
# Instalator bez stron Jezyk / Klawiatura / Strefa czasowa (system ma juz pl_PL, klawiature pl i Europe/Warsaw - zmiana pozniej w Konfiguracji)
if [ -e /etc/nd18e-skip-pages ]; then
  for s in /etc/calamares/settings.conf; do
    [ -f "$s" ] && sed -i -E '/^\s*-\s*"?(welcome|locale|keyboard|localecfg)(@[A-Za-z0-9_.-]+)?"?\s*(#.*)?$/d' "$s"
  done
  rm -f /etc/nd18e-skip-pages
fi
# Instalator w menu: nazwa ND18E zamiast Debiana
for f in /usr/share/applications/*calamares*.desktop /usr/share/applications/install-debian*.desktop; do
  [ -f "$f" ] && sed -i '/^Name\[/d; s/^Name=.*/Name=Zainstaluj ND18E Linux/' "$f"
done
# Sterownik NVIDIA (seria Pascal, GTX 1050 Ti) i mikrokod Intela (i5-7400)
apt-get install -y nvidia-driver intel-microcode || true
# dkms w chroot buduje dla kernela hosta - zbuduj dla kernela ISO
for k in /lib/modules/*; do dkms autoinstall -k "$(basename "$k")" || true; done
dpkg --configure -a || true
# kontrola: czy modul NVIDIA zostal zbudowany (szukaj w logu budowania linii "ND18E:")
for k in /lib/modules/*; do
  if find "$k" -name 'nvidia*.ko*' 2>/dev/null | grep -q .; then echo "ND18E: modul NVIDIA zbudowany dla $(basename "$k")"; else echo "ND18E: UWAGA - brak modulu NVIDIA dla $(basename "$k")"; fi
done
systemctl enable NetworkManager 2>/dev/null || true
systemctl enable systemd-timesyncd 2>/dev/null || true
sed -i 's/^# *pl_PL.UTF-8/pl_PL.UTF-8/' /etc/locale.gen; locale-gen || true
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true
# Mniej procesow w tle
for s in ModemManager bluetooth avahi-daemon cups cups-browsed ssh cron anacron rsyslog e2scrub_all.timer apt-daily.timer apt-daily-upgrade.timer man-db.timer; do
  systemctl disable "$s" 2>/dev/null || true; systemctl mask "$s" 2>/dev/null || true
done
find /usr/share/doc -type f ! -name copyright -delete 2>/dev/null || true
rm -rf /usr/share/man/* /usr/share/info/* /var/cache/apt/*.bin
update-initramfs -u || true
EOF
chmod +x config/hooks/normal/0100-nd18e.hook.chroot

sudo lb build
cp live-image-amd64.hybrid.iso ../ND18E_Linux.iso
echo "Gotowe: ND18E_Linux.iso"
