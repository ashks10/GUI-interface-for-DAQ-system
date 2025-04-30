const int inputPin1 = 2;
const int inputPin2 = 3;
const int inputPin3 = 4;

volatile unsigned long pulseCount1 = 0;
volatile unsigned long pulseCount2 = 0;
volatile unsigned long pulseCount3 = 0;

unsigned long lastTime = 0;
const unsigned long interval = 10;  // 10ms interval

void setup() {
  Serial.begin(115200);

  pinMode(inputPin1, INPUT);
  pinMode(inputPin2, INPUT);
  pinMode(inputPin3, INPUT);

  attachInterrupt(digitalPinToInterrupt(inputPin1), countPulse1, RISING);
  attachInterrupt(digitalPinToInterrupt(inputPin2), countPulse2, RISING);
  attachInterrupt(digitalPinToInterrupt(inputPin3), countPulse3, RISING);
}

void loop() {
  unsigned long currentTime = millis();

  if (currentTime - lastTime >= interval) {
    noInterrupts();
    unsigned long count1 = pulseCount1;
    unsigned long count2 = pulseCount2;
    unsigned long count3 = pulseCount3;
    pulseCount1 = 0;
    pulseCount2 = 0;
    pulseCount3 = 0;
    interrupts();
   
    float frequency1 = count1 * 100.0;
    float frequency2 = count2 * 100.0;
    float frequency3 = count3 * 100.0;

    Serial.print("CH1: ");
    Serial.print(frequency1 / 1000.0, 3);
    Serial.print(" kHz | ");

    Serial.print("CH2: ");
    Serial.print(frequency2 / 1000.0, 3);
    Serial.print(" kHz | ");

    Serial.print("CH3: ");
    Serial.print(frequency3 / 1000.0, 3);
    Serial.println(" kHz");

    lastTime = currentTime;
  }
}

// Interrupt Service Routines (ISRs)
void countPulse1() {
  pulseCount1++;
}

void countPulse2() {
  pulseCount2++;
}

void countPulse3() {
  pulseCount3++;
}
