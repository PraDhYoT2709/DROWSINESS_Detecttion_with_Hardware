const int buzzerPin = 8;      // Buzzer connected to digital pin 8
bool isDrowsy = false;       // Status flag
unsigned long lastBlinkTime = 0; // Variable to store the last time the buzzer state was updated
long blinkInterval = 1;     // Interval for blinking (500 ms ON, 500 ms OFF)
int buzzerState = LOW;        // Current state of the buzzer

void setup() {
  Serial.begin(9600);        // Start serial communication
  pinMode(buzzerPin, OUTPUT);
  digitalWrite(buzzerPin, LOW); // Ensure buzzer is off initially
  buzzerState = LOW;          // Initialize buzzer state variable
}

void loop() {
  // === Serial Communication Handling ===
  // Check if serial data is available and process it IMMEDIATELY
  if (Serial.available() > 0) {
    char input = Serial.read();  // Read the incoming byte

    // Optional: Print the received data for debugging
    // Serial.print("Received: ");
    // Serial.println(input);

    if (input == '1') {
      // Only update if the status is changing to avoid unnecessary buzzer state changes
      if (!isDrowsy) {
         isDrowsy = true;
         Serial.println("Drowsy -> ON"); // Debug print
         // When becoming drowsy, immediately set the buzzer to ON and start the timer
         buzzerState = HIGH;
         digitalWrite(buzzerPin, buzzerState);
         lastBlinkTime = millis(); // Reset timer for the blinking pattern
      }
    } else if (input == '0') {
      // Only update if the status is changing
      if (isDrowsy) {
        isDrowsy = false;
        Serial.println("Drowsy -> OFF"); // Debug print
        // When no longer drowsy, turn buzzer OFF immediately
        buzzerState = LOW;
        digitalWrite(buzzerPin, buzzerState);
      }
    }
  }

  // === Non-Blocking Buzzer Control ===
  // Only manage blinking if isDrowsy is true
  if (isDrowsy) {
    // Check if it's time to toggle the buzzer state
    if (millis() - lastBlinkTime >= blinkInterval) {
      // Save the last time you blinked the LED
      lastBlinkTime = millis();

      // If the buzzer is off turn it on and vice-versa:
      if (buzzerState == LOW) {
        buzzerState = HIGH;
      } else {
        buzzerState = LOW;
      }

      // Set the buzzer with the updated state
      digitalWrite(buzzerPin, buzzerState);
    }
  }
  // If not drowsy, the serial handling already ensured the buzzerState is LOW
  // and digitalWrite(buzzerPin, LOW) is called when the state changes.
  // No blinking logic is needed here.
}