#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SERVO_COUNT 6

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

int currentAngle[SERVO_COUNT];
int targetAngle[SERVO_COUNT];

unsigned long lastStepMs = 0;
const int STEP_MS = 15;
const int STEP_DEG = 1;

#define SERVO_MIN 120   // 0°
#define SERVO_MAX 600   // 180°

String line = "";

int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVO_MIN, SERVO_MAX);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();

  pwm.begin();
  pwm.setPWMFreq(50);   // szervók
  delay(10);

  for (int i = 0; i < SERVO_COUNT; i++) {
    currentAngle[i] = 90;
    targetAngle[i]  = 90;
    pwm.setPWM(i, 0, angleToPulse(90));
  }

  Serial.println("READY PCA");
}

void loop() {
  // parancs olvasás
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(line);
      line = "";
    } else if (c != '\r') {
      line += c;
    }
  }

  // sima mozgatás
  unsigned long now = millis();
  if (now - lastStepMs >= STEP_MS) {
    lastStepMs = now;

    for (int i = 0; i < SERVO_COUNT; i++) {
      if (currentAngle[i] < targetAngle[i]) currentAngle[i] += STEP_DEG;
      else if (currentAngle[i] > targetAngle[i]) currentAngle[i] -= STEP_DEG;

      currentAngle[i] = constrain(currentAngle[i], 0, 180);
      pwm.setPWM(i, 0, angleToPulse(currentAngle[i]));
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

  Serial.print("OK PCA S");
  Serial.print(idx);
  Serial.print(" -> ");
  Serial.println(angle);
}