# ICS-43434 Frequenzmesser – Raspberry Pi Zero 2 W

Live-Frequenzanalyse eines ICS-43434 I²S-Mikrofons mit einem Raspberry Pi Zero 2 W.

Das Projekt basiert auf dem vorgesehenen Signalweg:

ICS-43434 → I²S → Raspberry Pi Zero 2 W → ALSA → Python/NumPy → FFT → Frequenz in Hz

## Hardware

- Raspberry Pi Zero 2 W
- ICS-43434 I²S-Mikrofon
- microSD-Karte
- Raspberry Pi OS Lite 64-bit
- Jumper-Kabel
- WLAN für die Einrichtung

## Verdrahtung

| ICS-43434 | Raspberry Pi Zero 2 W | Pin |
|---|---|---:|
| VDD / 3V | 3.3 V | 1 |
| GND | GND | 6 |
| L/R | GND | 6 |
| SCK / BCLK | GPIO18 / PCM_CLK | 12 |
| WS / LRCLK | GPIO19 / PCM_FS | 35 |
| SD / DOUT | GPIO20 / PCM_DIN | 38 |

L/R = GND bedeutet linker I²S-Kanal.

## Projektstruktur

```text
ics43434-frequenzmesser-zero2/
├── config/
│   └── ics43434.dts
├── scripts/
│   ├── install.sh
│   └── test_audio.py
├── src/
│   ├── main.py
│   ├── fft_detector.py
│   └── audio_capture.py
├── requirements.txt
├── .gitignore
└── README.md
```

## 1. Raspberry Pi OS

Mit Raspberry Pi Imager:

1. Raspberry Pi Zero 2 W auswählen.
2. Raspberry Pi OS Lite 64-bit auswählen.
3. WLAN konfigurieren.
4. Benutzer erstellen.
5. SSH aktivieren.
6. SD-Karte schreiben.
7. SD-Karte einsetzen.
8. Raspberry Pi starten.

Danach per SSH verbinden:

```bash
ssh DEINBENUTZER@raspberrypi.local
```

## 2. Repository klonen

```bash
git clone https://github.com/DEINNAME/ics43434-frequenzmesser-zero2.git
cd ics43434-frequenzmesser-zero2
```

## 3. Installation

Das Skript installiert die im Projekt benötigten Pakete, aktiviert I²S und installiert das Overlay.

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

Danach den Raspberry Pi neu starten:

```bash
sudo reboot
```

## 4. I²S prüfen

Nach dem Neustart:

```bash
dmesg | grep -i -E "i2s|ics434|audio"
lsmod | grep -E "i2s|ics434|snd_soc"
arecord -l
```

Es sollte eine Soundkarte mit `ICS43434` erscheinen.

Beispiel:

```text
card 0: ICS43434 [ICS43434], device 0: ...
```

oder:

```text
card 1: ICS43434 [ICS43434], device 0: ...
```

Die CARD-Nummer merken.

## 5. Audioaufnahme testen

Beispiel für `card 1`:

```bash
arecord -D hw:1,0 -c 2 -r 48000 -f S32_LE -d 10 test.wav
```

Bei `card 0` stattdessen:

```bash
arecord -D hw:0,0 -c 2 -r 48000 -f S32_LE -d 10 test.wav
```

Während der Aufnahme sprechen, klatschen oder einen Ton erzeugen.

Danach:

```bash
ls -lh test.wav
python3 scripts/test_audio.py test.wav
```

Die Werte Minimum, Maximum und RMS sollten sich bei einem Signal verändern.

## 6. Frequenzmesser starten

Die Soundkarten-Nummer wird beim Start als Argument übergeben.

Für `card 0`:

```bash
python3 src/main.py hw:0,0
```

Für `card 1`:

```bash
python3 src/main.py hw:1,0
```

Beispielausgabe:

```text
======================================
 ICS-43434 LIVE FFT
 Raspberry Pi Zero 2 W
======================================

Sample Rate : 48000 Hz
FFT         : 4096
Auflösung   : 11.71875 Hz

Frequenz:    433.6 Hz | Peak:       23145
Frequenz:    445.3 Hz | Peak:       25781
Frequenz:    433.6 Hz | Peak:       22143
```

## 7. FFT-Einstellungen

In `src/main.py`:

```python
SAMPLE_RATE = 48000
FFT_SIZE = 4096
CHANNELS = 2
CHANNEL = 0
```

Mit 48 kHz und 4096 Samples beträgt die FFT-Bin-Auflösung:

```text
48000 / 4096 = 11.71875 Hz
```

Mit 8192 Samples:

```text
48000 / 8192 = 5.859375 Hz
```

Eine größere FFT verbessert die Frequenzauflösung, benötigt aber mehr Daten und Rechenzeit.

## 8. GitHub-Workflow

Änderungen übernehmen:

```bash
git add .
git commit -m "Frequenzanalyse aktualisiert"
git push
```

Der Kumpel kann den aktuellen Stand anschließend holen:

```bash
git pull
```

## Hinweise

- Der ICS-43434 wird über I²S und nicht über I²C ausgelesen.
- Die relevanten Signale sind SCK/BCLK, WS/LRCLK und SD/DOUT.
- Die Frequenzanzeige zeigt die dominante Frequenz des ausgewählten Kanals.
- Die tatsächliche Soundkarten-Nummer muss aus `arecord -l` übernommen werden.
- Dieses Repository folgt der bereitgestellten Projektbeschreibung für den Raspberry Pi Zero 2 W.
