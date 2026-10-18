// esp32_expense_logger.ino
// OPTIONAL hardware extension from the project brief.
// Three buttons log food and travel expenses to the Serial Monitor.
//
// STATUS: NOT TESTED. This sketch was written for the brief and has not been run on an ESP32.
// It only prints to the Serial Monitor. It does NOT write to expenses.csv.
// Amounts are written as "Rs." instead of the rupee sign, to avoid character problems in Arduino.

const int foodBtn = 4;     // GPIO 4  -> logs Rs. 100 to Food
const int travelBtn = 5;   // GPIO 5  -> logs Rs. 150 to Travel
const int resetBtn = 18;   // GPIO 18 -> resets the session counts

int foodCount = 0;
int travelCount = 0;

void setup() {
  Serial.begin(115200);
  pinMode(foodBtn, INPUT);
  pinMode(travelBtn, INPUT);
  pinMode(resetBtn, INPUT);
  Serial.println("Expense Logger Started");
}

void loop() {
  if (digitalRead(foodBtn) == HIGH) {
    foodCount++;
    Serial.println("Expense Logged: Food - Rs. 100");
    delay(300);                       // simple debounce
  }
  if (digitalRead(travelBtn) == HIGH) {
    travelCount++;
    Serial.println("Expense Logged: Travel - Rs. 150");
    delay(300);
  }
  if (digitalRead(resetBtn) == HIGH) {
    foodCount = 0;
    travelCount = 0;
    Serial.println("Session Reset");
    delay(500);
  }
}
