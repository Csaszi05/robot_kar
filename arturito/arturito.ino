#include <Servo.h>

const int SERVO_COUNT = 6;
Servo servos[SERVO_COUNT];
int servoPins[SERVO_COUNT] = {3, 5, 6, 9, 10, 11}; // állítsd a saját pinjeidre

int currentAngle[SERVO_COUNT];
int targetAngle[SERVO_COUNT];

unsigned long lastStepMs = 0;
const int STEP_MS = 15;   // nagyobb = lassabb (pl. 20–30)
const int STEP_DEG = 1;   // lépésméret fokban (1 = szép sima)

String line = "";

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(servoPins[i]);
    currentAngle[i] = 90;
    targetAngle[i]  = 90;
    servos[i].write(90);
  }

  Serial.println("READY");
}

void loop() {
  // 1) Parancsok olvasása
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(line);
      line = "";
    } else if (c != '\r') {
      line += c;
    }
  }

  // 2) Szervók lassú mozgatása a cél felé
  unsigned long now = millis();
  if (now - lastStepMs >= STEP_MS) {
    lastStepMs = now;

    for (int i = 0; i < SERVO_COUNT; i++) {
      if (currentAngle[i] < targetAngle[i]) {
        currentAngle[i] += STEP_DEG;
      } else if (currentAngle[i] > targetAngle[i]) {
        currentAngle[i] -= STEP_DEG;
      }

      currentAngle[i] = constrain(currentAngle[i], 0, 180);
      servos[i].write(currentAngle[i]);
    }
  }
}

void handleLine(String cmd) {
  cmd.trim(); // pl: S2:120
  if (cmd.length() < 4) return;
  if (cmd[0] != 'S') return;

  int colonPos = cmd.indexOf(':');
  if (colonPos < 0) return;

  int idx = cmd.substring(1, colonPos).toInt();
  int angle = cmd.substring(colonPos + 1).toInt();

  if (idx < 0 || idx >= SERVO_COUNT) return;
  angle = constrain(angle, 0, 180);

  targetAngle[idx] = angle;

  Serial.print("OK S");
  Serial.print(idx);
  Serial.print(" -> ");
  Serial.println(angle);
}