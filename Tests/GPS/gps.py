import time
import serial
from micropygps import MicropyGPS
# 1. Seriellen Port für den Pi Zero 2 W konfigurieren
# /dev/serial0 verweist automatisch auf die GPIO-Pins 14 (TX) und 15 (RX).
SERIAL_PORT = '/dev/serial0'
BAUD_RATE = 9600
# GPS-Parser und serielle Verbindung initialisieren
gps = MicropyGPS()
gps_serial = serial.Serial(SERIAL_PORT, baudrate=BAUD_RATE, timeout=1)
print("GPS-Modul gestartet. Warte auf gültige Satelliten-Daten...")
# 2. Endlosschleife zur Datenverarbeitung
try:
   while True:
       # Prüfen, ob Daten vom GPS-Modul im Puffer liegen
       if gps_serial.in_waiting > 0:
           # Daten lesen und decodieren (Fehlerhafte Zeichen ignorieren)
           data = gps_serial.read(gps_serial.in_waiting).decode('utf-8', errors='ignore')

           # Daten Zeichen für Zeichen in den Parser einspeisen
           for char in data:
               gps.update(char)

           # Breitengrad (Latitude) berechnen
           # micropygps liefert eine Liste: [Grad, Dezimalminuten]
           lat_deg = gps.latitude[0] + (gps.latitude[1] / 60.0)
           if gps.validity and gps.latitude_direction == 'S':
               lat_deg = -lat_deg

           # Längengrad (Longitude) berechnen
           lng_deg = gps.longitude[0] + (gps.longitude[1] / 60.0)
           if gps.validity and gps.longitude_direction == 'W':
               lng_deg = -lng_deg
           # Ausgabe im Terminal, sobald ein gültiges Signal (Fix) da ist
           if lat_deg != 0.0 and lng_deg != 0.0:
               print(f"latitude: {lat_deg:.6f}")
               print(f"longitude: {lng_deg:.6f}")
               print("-" * 25) # Trennlinie für bessere Lesbarkeit

       time.sleep(0.5) # Schont die CPU des Pi Zero
except KeyboardInterrupt:
   print("\nProgramm abgebrochen.")
   gps_serial.close()