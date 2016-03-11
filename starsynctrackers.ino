//
// Need AccelStepper fork with AFMotor support with library 
//   https://github.com/adafruit/AccelStepper
// If using Adafruit v2 Motorshield requires the Adafruit_Motorshield v2 library 
//   https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library
// if using adafruit motor shield v1 then you need v1 library
//' https://github.com/adafruit/Adafruit-Motor-Shield-library

#include <AccelStepper.h>
#include <Wire.h>


// STEPPER_DRIVER
// 0 - Adafruit Motorshield V2 https://www.adafruit.com/products/1438
// 1 - Easy Driver https://www.sparkfun.com/products/12779 (http://www.schmalzhaus.com/EasyDriver/index.html)
// 2 - Adafruit Motorshield V1 https://www.adafruit.com/products/81
// 3 - Big Easy Driver https://www.sparkfun.com/products/12859 (http://www.schmalzhaus.com/BigEasyDriver/)
#define STEPPER_DRIVER 3


//Constants
static const float STEPS_PER_ROTATION = 200.0; // Steps per rotation, just steps not microsteps.
static const float THREADS_PER_INCH = 20;  // Threads per inch or unit of measurement
static const float R_I = 7.3975;     // Distance from plate pivot to rod when rod is perp from plate // Russ: 7.28
static const float D_S = 0.00591;   // Distance from rod pivot to plate
static const float D_F = 0.650; // Distiance along rod from plate to starting position // Russ: 0.432
static const float RECALC_INTERVAL_S = 15; // Time in seconds between recalculating

// STOP_TYPE
// 0 for switch button type
// 1 for analog proximity type
#define STOP_TYPE 1
static const int STOP_ANALOG_POWER_PIN = 10; //Pins stop switch gets power from, Digital pins only.
static const int STOP_ANALOG_POWER_STOP_VALUE = 800; // 0 - 1023 (0 closer, 1023 farther)
static const int STOP_BUTTON_PIN = A4;      // The pin the stop push switch is on
static const int STOP_BUTTON_TYPE = 1;     // The type of switch 0 - Normally Closed; 1 - Normally Open
static const float DIRECTION = 1.0; // 1 forward is forward; -1 + is forward is backward


#include "stepper_drivers.h"

#if STOP_TYPE == 1
void stop_button_analog_power(boolean powered) {
  if (powered) {
    digitalWrite(STOP_ANALOG_POWER_PIN, HIGH);
  } else {
    digitalWrite(STOP_ANALOG_POWER_PIN, LOW);    
  }
}
#endif


void setup()
{  
  Serial.begin(9600);           // set up Serial library at 9600 bps
  Serial.println("Star Tracker v0.01");

#if STOP_TYPE == 0
  pinMode(STOP_BUTTON_PIN, INPUT_PULLUP);
#else
  pinMode(STOP_ANALOG_POWER_PIN, OUTPUT);
#endif

#if STEPPER_DRIVER == 0
  AFMS.begin();  // create with the default frequency 1.6KHz
#endif

  //while(true) {
  //  reset_lp();
  //}

  goInitialPosition();
  Astepper1.setCurrentPosition(0);
}


void goInitialPosition() 
{
  Serial.println("goInitialPosition");
  delay(250);

#if STOP_TYPE == 0
  int buttonV = digitalRead(STOP_BUTTON_PIN);
  while (buttonV == STOP_BUTTON_TYPE)
#else
  int count = 0;
  stop_button_analog_power(true);
  delay(100);
  int buttonV = analogRead(STOP_BUTTON_PIN);
  //buttonV=1000;
  while (buttonV > STOP_ANALOG_POWER_STOP_VALUE)
#endif
  {
    reset_lp();

#if STOP_TYPE == 0
    buttonV = digitalRead(STOP_BUTTON_PIN);
#else
    count++;
    if(count > 20 || (count > 5 && buttonV < STOP_ANALOG_POWER_STOP_VALUE+50)) {
      buttonV = analogRead(STOP_BUTTON_PIN); //TODO: Does analog read greatly slow down reset
      count = 0;
    }
#endif
  }
  reset_done();
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
#if STOP_TYPE == 1
  stop_button_analog_power(false);
#endif
  Serial.println("At initial position");
  delay(250);
  Serial.println("goInitialPosition end");
}

static unsigned long time_solar_start_ms = 0;  // Initial starting time.
static float time_solar_last_s = -RECALC_INTERVAL_S; //Last solar time we recalculated steps 
static float theta_initial = atan(D_F/R_I);


float tracker_calc_rod_length(float theta) {
  float psi, r, d;
  
  psi = 0.5*(PI - theta);
  r = R_I - D_S * tan(PI / 2.0 - psi); //Calculated adjusted length from pivot to center of rod
  d = r * sin(theta) / sin(psi); //Calculates desired length of rod between plates.
  return d;
}

static float d_initial = tracker_calc_rod_length(theta_initial);


float tracker_calc_steps(float time_solar_s) {
  float time_sidereal_s, theta, d, total_steps;
  
  time_sidereal_s = time_solar_s * 1.0027379;  //Calculates sidereal time from solar time.
  theta = theta_initial + 0.25 * PI * time_sidereal_s / 10800.0; //Calculates desired plate pivot angle
  d = tracker_calc_rod_length(theta);
  total_steps = MICROSTEPS * (d-d_initial) * STEPS_PER_ROTATION * THREADS_PER_INCH; //Calculates total steps we should be at, at given time.
  return total_steps;
}

void loop()
{
  float time_solar_s, spd, time_diff_s, steps_wanted;
  
  if (time_solar_start_ms == 0) {
    time_solar_start_ms = millis();
  }
  time_solar_s = ((float)(millis() - time_solar_start_ms))/1000.0;
  time_diff_s = time_solar_s - time_solar_last_s;
  if (time_diff_s >= RECALC_INTERVAL_S) {
    time_solar_last_s = time_solar_s;
    steps_wanted = tracker_calc_steps(time_solar_s + RECALC_INTERVAL_S/2.0);
    spd = (steps_wanted - DIRECTION*Astepper1.currentPosition())/(RECALC_INTERVAL_S/2);
    Astepper1.setSpeed(DIRECTION*spd);
    Serial.println(spd);
  }
  Astepper1.runSpeed();
}

