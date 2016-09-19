
#include "stepper_drivers.h"
#include "starsynctrackers.h"

extern SSTVARS sstvars;

boolean reset_started = false;

#if STEPPER_DRIVER == 0

Adafruit_MotorShield AFMS;
Adafruit_StepperMotor* myStepper1;

void stepper_init() {
  // Create the motor shield object with the default I2C address
  AFMS = Adafruit_MotorShield();
  // Or, create it with a different I2C address (say for stacking)
  // Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

  // create with the default frequency 1.6KHz
  AFMS.begin(); 
  
  // motor port #1 M1 and M2
  myStepper1 = AFMS.getStepper(sstvars.stepsPerRotation, 1);
  // motor port #2 (M3 and M4)
  //*myStepper1 = AFMS.getStepper(sstvars.stepsPerRotation, 2);
  
}

// you can change these to DOUBLE or INTERLEAVE or MICROSTEP!
void stepper_forwardstep1() {
  myStepper1->onestep(FORWARD, MICROSTEP);
}
void stepper_backwardstep1() {  
  myStepper1->onestep(BACKWARD, MICROSTEP);
}

AccelStepper Astepper1(stepper_forwardstep1, stepper_backwardstep1); // use functions to step

unsigned long reset_start_ms = 0.0;
unsigned long reset_diff_ms = 0.0;
unsigned long reset_count = 0;
void stepper_reset_lp() {
  myStepper1->onestep(BACKWARD, DOUBLE);
  delayMicroseconds(300);
}

void stepper_reset_done() {
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
}

#endif

#if STEPPER_DRIVER == 1

AccelStepper Astepper1(1, 9, 8);

void stepper_init() {
  
}

void stepper_reset_lp() {
  if (!reset_started) {
    reset_started = true;
    if (sstvars.dir > 0) {
      digitalWrite(8, HIGH);
    }
  }
  digitalWrite(9, HIGH);
  delayMicroseconds(150);
  digitalWrite(9, LOW);
  delayMicroseconds(150);
}

void stepper_reset_done() {
  digitalWrite(8, LOW);
}

#endif


#if STEPPER_DRIVER == 2

#include <AFMotor.h>
AF_Stepper myStepper1(sstvars.stepsPerRotation, 1);


void stepper_init() { 
}

// you can change these to DOUBLE or INTERLEAVE or MICROSTEP!
void stepper_forwardstep1() {
  myStepper1.onestep(FORWARD, MICROSTEP);
}
void stepper_backwardstep1() {  
  myStepper1.onestep(BACKWARD, MICROSTEP);
}

AccelStepper Astepper1(stepper_forwardstep1, stepper_backwardstep1); // use functions to step

void stepper_reset_lp() {
  myStepper1->onestep(BACKWARD, DOUBLE);
  delayMicroseconds(300);
}

void stepper_reset_done() {
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
}

#endif

#if STEPPER_DRIVER == 3

AccelStepper Astepper1(1, 9, 8);

void stepper_init() {  
}

int reset_lp_loop = 0;
void stepper_reset_lp() {
  if (!reset_started) {
    reset_started = true;
    if (sstvars.dir > 0) {
      digitalWrite(8, LOW);
    } else {
      digitalWrite(8, HIGH);
    }
  }
  reset_lp_loop = 0;
  while(reset_lp_loop < 1) {
    digitalWrite(9, HIGH);
    delayMicroseconds(75);
    digitalWrite(9, LOW);
    delayMicroseconds(75);
    reset_lp_loop++;
  }
}

void stepper_reset_done() {
  digitalWrite(8, LOW);
}

#endif




