// ============================================================
// ICS-43434 -> Arduino UNO R3
//
// ICS-43434:
// VDD  -> 3.3V
// GND  -> GND
// LR   -> GND
// WS   -> D13
// SCK  -> D6
// SD   -> D7
//
// Ausgabe: dominante Frequenz in Hz
//
// Serial Monitor: 115200 Baud
// ============================================================

#define WS_PIN    13
#define BCLK_PIN  6
#define DATA_PIN  7

// Arduino UNO:
// D6  = PD6
// D7  = PD7
// D13 = PB5

#define BCLK_HIGH() (PORTD |=  _BV(PD6))
#define BCLK_LOW()  (PORTD &= ~_BV(PD6))

#define WS_HIGH()   (PORTB |=  _BV(PB5))
#define WS_LOW()    (PORTB &= ~_BV(PB5))

#define DATA_READ() (PIND & _BV(PD7))


// ============================================================
// EIN BCLK
//
// Ziel: ungefähr 1 MHz BCLK
// -> ungefähr 16 kHz Audio-Samplerate
//
// 16 MHz Arduino-Takt
// ============================================================

static inline void bclk()
{
  BCLK_HIGH();

  asm volatile(
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
  );

  BCLK_LOW();

  asm volatile(
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
    "nop\n\t"
  );
}


// ============================================================
// LINKEN ICS-43434 KANAL LESEN
//
// Ein WS-Rahmen besteht aus:
// 32 BCLK = LEFT
// 32 BCLK = RIGHT
//
// Beim linken Kanal:
// 1 Takt I2S-Verzögerung
// danach 24 Datenbits
// danach 7 Restbits
// ============================================================

int32_t readLeft()
{
  uint32_t value = 0;


  // ----------------------------------------------------------
  // WS = LEFT
  // ----------------------------------------------------------

  WS_LOW();


  // I2S: ein BCLK vor dem ersten Datenbit
  bclk();


  // ----------------------------------------------------------
  // 24 Bit lesen
  // ----------------------------------------------------------

  for (uint8_t i = 0; i < 24; i++)
  {
    BCLK_HIGH();

    asm volatile(
      "nop\n\t"
      "nop\n\t"
      "nop\n\t"
    );

    value <<= 1;

    if (DATA_READ())
      value |= 1;

    BCLK_LOW();

    asm volatile(
      "nop\n\t"
      "nop\n\t"
      "nop\n\t"
    );
  }


  // ----------------------------------------------------------
  // restliche 7 BCLK des linken 32-Bit-Slots
  // ----------------------------------------------------------

  for (uint8_t i = 0; i < 7; i++)
  {
    bclk();
  }


  // ----------------------------------------------------------
  // RIGHT CHANNEL
  //
  // Wir haben nur ein Mikrofon mit LR = GND.
  // Trotzdem müssen die 32 BCLK erzeugt werden.
  // ----------------------------------------------------------

  WS_HIGH();

  for (uint8_t i = 0; i < 32; i++)
  {
    bclk();
  }


  // ----------------------------------------------------------
  // 24-Bit signed -> 32-Bit signed
  // ----------------------------------------------------------

  if (value & 0x00800000UL)
  {
    value |= 0xFF000000UL;
  }

  return (int32_t)value;
}


// ============================================================
// SETUP
// ============================================================

void setup()
{
  Serial.begin(115200);

  // D6 Ausgang
  DDRD |= _BV(PD6);

  // D7 Eingang
  DDRD &= ~_BV(PD7);

  // D13 Ausgang
  DDRB |= _BV(PB5);

  BCLK_LOW();
  WS_LOW();

  delay(1000);

  Serial.println();
  Serial.println(F("ICS-43434 Frequenzmessung"));
  Serial.println(F("-------------------------"));
  Serial.println(F("Samplerate ca. 16 kHz"));
  Serial.println(F("BCLK ca. 1 MHz"));
  Serial.println(F("Baudrate 115200"));
  Serial.println();
}


// ============================================================
// FREQUENZMESSUNG
//
// Wir messen 256 Samples.
//
// Das reicht fuer eine einfache Frequenzbestimmung.
// ============================================================

void loop()
{
  const uint16_t NUM_SAMPLES = 256;

  // Bei ca. 16 kHz dauern 256 Samples etwa 16 ms.
  //
  // Wir bestimmen:
  // - Mittelwert
  // - positive Nulldurchgaenge


  long sum = 0;

  int32_t samples[256];


  // ----------------------------------------------------------
  // Samples aufnehmen
  // ----------------------------------------------------------

  for (uint16_t i = 0; i < NUM_SAMPLES; i++)
  {
    int32_t s = readLeft();

    // 24 Bit -> ungefähr 16 Bit
    s >>= 8;

    samples[i] = s;

    sum += s;
  }


  // ----------------------------------------------------------
  // DC-Mittelwert berechnen
  // ----------------------------------------------------------

  int32_t average = sum / NUM_SAMPLES;


  // ----------------------------------------------------------
  // Nulldurchgaenge suchen
  // ----------------------------------------------------------

  uint16_t crossings = 0;

  int32_t previous = samples[0] - average;


  // Schwelle gegen Mikrofonrauschen
  const int32_t THRESHOLD = 200;


  for (uint16_t i = 1; i < NUM_SAMPLES; i++)
  {
    int32_t current = samples[i] - average;


    // negativer -> positiver Übergang
    if (previous < -THRESHOLD &&
        current >= THRESHOLD)
    {
      crossings++;
    }


    previous = current;
  }


  // ----------------------------------------------------------
  // Frequenz berechnen
  //
  // 256 Samples bei ca. 16 kHz
  // ----------------------------------------------------------

  float sampleRate = 16000.0;

  float frequency =
    ((float)crossings * sampleRate) /
    (2.0 * NUM_SAMPLES);


  // ----------------------------------------------------------
  // Ausgabe
  // ----------------------------------------------------------

  Serial.print(F("Frequenz: "));

  if (frequency < 20.0)
  {
    Serial.println(F("0 Hz"));
  }
  else
  {
    Serial.print(frequency, 1);
    Serial.println(F(" Hz"));
  }


  delay(500);
}

