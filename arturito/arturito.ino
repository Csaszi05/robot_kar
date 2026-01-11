#include <Servo.h>

const int SERVO_COUNT = 6;
Servo servos[SERVO_COUNT];
int servoPins[SERVO_COUNT] = {3, 5, 6, 9, 10, 11}; // állítsd a saját pinjeidre

String line = "";

void setup() {
  Serial.begin(115200);

  for (int i = 0; i < SERVO_COUNT; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(90);
  }

  Serial.println("READY");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      handleLine(line);
      line = "";
    } else if (c != '\r') {
      line += c;
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

  servos[idx].write(angle);

  Serial.print("OK S");
  Serial.print(idx);
  Serial.print(" ");
  Serial.println(angle);
}