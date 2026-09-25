#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BOOT_CONFIG="/boot/firmware/config.txt"
OVERLAY_DIR="/boot/firmware/overlays"
OVERLAY_SRC="$PROJECT_DIR/config/ics43434.dts"
OVERLAY_DTB="/tmp/ics43434.dtbo"

echo "=== ICS-43434 / Raspberry Pi Zero 2 W Installation ==="

echo "[1/6] Paketquellen aktualisieren..."
sudo apt update

echo "[2/6] Benötigte Pakete installieren..."
sudo apt install -y \
    device-tree-compiler \
    alsa-utils \
    python3 \
    python3-numpy

echo "[3/6] I²S aktivieren..."
if ! grep -q '^dtparam=i2s=on$' "$BOOT_CONFIG"; then
    echo 'dtparam=i2s=on' | sudo tee -a "$BOOT_CONFIG" >/dev/null
fi

echo "[4/6] Device-Tree-Overlay kompilieren..."
dtc -@ -I dts -O dtb \
    -o "$OVERLAY_DTB" \
    "$OVERLAY_SRC"

echo "[5/6] Overlay installieren..."
sudo cp "$OVERLAY_DTB" "$OVERLAY_DIR/ics43434.dtbo"

echo "[6/6] Overlay in config.txt aktivieren..."
if ! grep -q '^dtoverlay=ics43434$' "$BOOT_CONFIG"; then
    echo 'dtoverlay=ics43434' | sudo tee -a "$BOOT_CONFIG" >/dev/null
fi

echo
echo "Installation abgeschlossen."
echo "Jetzt neu starten mit:"
echo
echo "    sudo reboot"
echo
echo "Danach prüfen mit:"
echo
echo "    arecord -l"
