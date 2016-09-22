//
// Need AccelStepper fork with AFMotor support with library 
//   https://github.com/adafruit/AccelStepper
// If using Adafruit v2 Motorshield requires the Adafruit_Motorshield v2 library 
//   https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library
// if using adafruit motor shield v1 then you need v1 library
//' https://github.com/adafruit/Adafruit-Motor-Shield-library

#include <AccelStepper.h>
#include <Wire.h>
#include <EEPROM.h>
#include <avr/pgmspace.h>
#include <stdint.h>

#include "starsynctrackers.h"
#include "sst_console.h"
#include "stepper_drivers.h"

const char* sstversion = "v1.1.0";


// Default constant EEPROM values
static const uint16_t EEPROM_MAGIC = 0x0101;
static const float STEPS_PER_ROTATION = 200.0; // Steps per rotation, just steps not microsteps.
static const float THREADS_PER_INCH = 20;  // Threads per inch or unit of measurement
static const float R_I = 7.3975;     // Distance from plate pivot to rod when rod is perp from plate // Russ: 7.28
static const float D_S = 0.00591;   // Distance from rod pivot to plate
static const float D_F = 0.446; // Distiance along rod from plate to starting position // Russ: 0.432
static const float RECALC_INTERVAL_S = 15; // Time in seconds between recalculating
static const float END_LENGTH_RESET = 6.500; // Length to travel before reseting.
static const float DIRECTION = 1.0; // 1 forward is forward; -1 + is forward is backward

// STOP_TYPE
// 0 for switch button type
// 1 for analog proximity type
#define STOP_TYPE 1
static const int STOP_ANALOG_POWER_PIN = 10; //Pins stop switch gets power from, Digital pins only.
static const int STOP_ANALOG_POWER_STOP_VALUE = 800; // 0 - 1023 (0 closer, 1023 farther)
static const int STOP_BUTTON_PIN = A2;      // The pin the stop push switch is on
static const int STOP_BUTTON_TYPE = 1;     // The type of switch 0 - Normally Closed; 1 - Normally Open

bool keep_running = true;
float sst_rate = 1.0;
int sst_reset_count = 0;
SSTVARS sstvars;
float time_diff_s = 0;
float time_adjust_s = 0;
float time_solar_last_s; //Last solar time we recalculated steps 

boolean sst_debug = false;

unsigned long time_solar_start_ms;  // Initial starting time.
static float theta_initial;
static float d_initial;

static void sst_eeprom_init(void);
static float tracker_calc_steps(float time_solar_s);
void check_end(float current_steps);


#if STOP_TYPE == 1
void stop_button_analog_power(boolean powered) {
  if (powered) {
    digitalWrite(STOP_ANALOG_POWER_PIN, HIGH);
  } else {
    digitalWrite(STOP_ANALOG_POWER_PIN, LOW);    
  }
}
#endif

/**
 * If the EEPROM has not be been initialized, it will init it. If it has been set it sets 
 * struct sstvars with the contents of the EEPROM.
 */
static void sst_eeprom_init() {
  //Since arduino doesn't load eeprom set with EEMEM, do our own init.
  uint16_t magic;
  EEPROM.get(0, magic);
  if (magic != EEPROM_MAGIC) {
    //Initial EEPROM
    EEPROM.put(0, magic);
    sstvars.stepsPerRotation = STEPS_PER_ROTATION;
    sstvars.threadsPerInch = THREADS_PER_INCH;
    sstvars.r_i = R_I;
    sstvars.d_s = D_S;
    sstvars.d_f = D_F;
    sstvars.recalcIntervalS = RECALC_INTERVAL_S;
    sstvars.endLengthReset = END_LENGTH_RESET;
    sstvars.dir = DIRECTION;
    sst_save_sstvars();
  } else {
    //Read in from EEPROM
    EEPROM.get(sizeof(uint16_t), sstvars);
  }
}

// See starsynctrackers.h
void sst_save_sstvars() {
    EEPROM.put(sizeof(uint16_t), sstvars); 
}

/**
 * When first powered up. sets up serial, sstvars, stepper, console, resets tracker.
 */
void setup()
{  
  Serial.begin(115200);           // set up Serial library at 9600 bps
  Serial.print(F("Star Tracker "));
  Serial.println(sstversion);

  sst_eeprom_init();

#if STOP_TYPE == 0
  pinMode(STOP_BUTTON_PIN, INPUT_PULLUP);
#else
  pinMode(STOP_ANALOG_POWER_PIN, OUTPUT);
#endif

  stepper_init();

  //while(true) {
  //  stepper_reset_lp();
  //}
  sst_console_init();

  sst_reset();
}

// See starsynctrackers.h
void sst_reset() 
{
  if (sst_debug) {
    Serial.println(F("sst_reset"));
  }
  delay(250);
  sst_reset_count++;
  reset_started = false;

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
    stepper_reset_lp();

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
  stepper_reset_done();
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
#if STOP_TYPE == 1
  stop_button_analog_power(false);
#endif
  if (sst_debug) {
    Serial.println(F("At initial position"));
  }
  delay(250);
  time_solar_start_ms = 0;
  time_solar_last_s = -sstvars.recalcIntervalS;
  theta_initial = atan(sstvars.d_f/sstvars.r_i);
  d_initial = sst_rod_length_by_angle(theta_initial);
  time_adjust_s = 0;
  Astepper1.setCurrentPosition(0);
  // Max speed a eeprom value
  Astepper1.setMaxSpeed(10000);
  if (sst_debug) {
    Serial.println(F("sst_reset end"));
  }
}

// See starsynctrackers.h
float sst_rod_length_by_angle(float theta) {
  float psi, r, d;
  
  psi = 0.5*(PI - theta);
  r = sstvars.r_i - sstvars.d_s * tan(PI / 2.0 - psi); //Calculated adjusted length from pivot to center of rod
  d = r * sin(theta) / sin(psi); //Calculates desired length of rod between plates.
  return d;
}

// See starsynctrackers.h
float sst_theta(float time_solar_s) {
  float time_sidereal_s;
  
  time_sidereal_s = sst_rate*time_solar_s * 1.0027379;  //Calculates sidereal time from solar time.
  return (theta_initial + 0.25 * PI * time_sidereal_s / 10800.0); //Calculates desired plate pivot angle
}

/**
 * Steps the tracker should be set to if ran for a time.
 * @param time_solar_s Time in seconds of run time.
 * @return Steps the tracker should be at, at time.
 */
static float tracker_calc_steps(float time_solar_s) {
  float theta, d, total_steps;
  
  theta = sst_theta(time_solar_s);
  if(sst_debug) {
    Serial.print("theta=");
    Serial.println(theta,5);
  }
  d = sst_rod_length_by_angle(theta);
  total_steps = MICROSTEPS * (d-d_initial) * sstvars.stepsPerRotation * sstvars.threadsPerInch; //Calculates total steps we should be at, at given time.
  return total_steps;
}

 // See starsynctrackers.h
float steps_to_time_solar(float current_steps) {
  //Secant method
  //http://www.codewithc.com/c-program-for-secant-method/
  float a=millis()/1000.0;
  float b=0;
  float c= 0;
  float fa = 0;
  float fb = 0;
  do
  {
    fb = tracker_calc_steps(b) - current_steps;
    fa = tracker_calc_steps(a) - current_steps;
    c=(a*fb - b*fa)/(fb-fa);
    a = b;
    b = c;
  } while(fabs(tracker_calc_steps(c) - current_steps) > 1);
  if (sst_debug) {
    Serial.print("c =");
    Serial.println(c);
  }
  return c;
}

// See starsynctrackers.h
float rod_length_to_solar(float d) {
  //Steps needed to get to d
  float steps = (d-d_initial)*MICROSTEPS*sstvars.stepsPerRotation*sstvars.threadsPerInch;
  return steps_to_time_solar(steps);
}

// See starsynctrackers.h
float sst_rod_length_by_steps(float current_steps) {
  return ((current_steps / (MICROSTEPS * sstvars.stepsPerRotation * sstvars.threadsPerInch)) + d_initial);
}

/**
 * Given current steps if at endLengthReset will run tracker reset.
 * @param current_steps steps
 */
static void check_end(float current_steps) {
  if (sst_rod_length_by_steps(current_steps) >= sstvars.endLengthReset) {
    sst_reset();
  }
}

static int loop_count = 0;
/**
 * Program loop.
 */
void loop()
{
  float time_solar_s, spd, steps_wanted;
  loop_count++;

  if (time_solar_start_ms == 0) {
    time_solar_start_ms = millis();
  }
  time_solar_s = ((float)(millis() - time_solar_start_ms))/1000.0 + time_adjust_s;
  //if(loop_count > 10000) {
    //Serial.println(time_solar_s, 8);
   // loop_count = 0;
  //}
  time_diff_s = time_solar_s - time_solar_last_s;

  if (!keep_running) {
    delay(10);
  } else {  
    if (time_diff_s >= RECALC_INTERVAL_S) {
      time_solar_last_s = time_solar_s;
      if(sst_debug) {
        Serial.print(tracker_calc_steps(time_solar_s));
        Serial.print(",");
        Serial.println(Astepper1.currentPosition());
      }
      steps_wanted = tracker_calc_steps(time_solar_s + RECALC_INTERVAL_S);
      spd = (steps_wanted - sstvars.dir*Astepper1.currentPosition())/(RECALC_INTERVAL_S);
      Astepper1.setSpeed(sstvars.dir*spd);
      if(sst_debug) {
        Serial.println(spd);
      }
    }
    Astepper1.runSpeed();
//    int i = 0;
//    for(i = 0; i < 66; i++) {
 //     delayMicroseconds(75);
  //  }
    check_end(sstvars.dir*Astepper1.currentPosition());
  }
  sst_console_read_serial();
}

