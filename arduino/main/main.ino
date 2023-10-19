#include <ArduinoJson.h>

const int releChPos[8] = {10, 11, 12, A0, A1, A2, A3, A4};
int lampStates[8] = {LOW, LOW, LOW, LOW, LOW, LOW, LOW, LOW};

DynamicJsonDocument doc(200);

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < 8; i++) {
    pinMode(releChPos[i], OUTPUT);
    digitalWrite(releChPos[i], lampStates[i]);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String jsonStr = Serial.readStringUntil('\n');
    deserializeJson(doc, jsonStr);

    int lampId = doc["lamp_id"];
    if (lampId >= 1 && lampId <= 8) {
      int newState = doc["state"];
      lampStates[lampId - 1] = newState;
      digitalWrite(releChPos[lampId - 1], newState);
    }
  }
}

