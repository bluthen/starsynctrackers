#ifndef __STEPPER_DRIVERS_H
#define __STEPPER_DRIVERS_H

#if STEPPER_DRIVER == 0

#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

// Connect a stepper motor with 200 steps per revolution (1.8 degree)
// to motor port #2 (M3 and M4)
//Adafruit_StepperMotor *myStepper1 = AFMS.getStepper(STEPS_PER_ROTATION, 2);

//motor port #1 M1 and M2
Adafruit_StepperMotor *myStepper1 = AFMS.getStepper(STEPS_PER_ROTATION, 1);

// you can change these to DOUBLE or INTERLEAVE or MICROSTEP!
void forwardstep1() {
  if (DIRECTION > 0) {  
    myStepper1->onestep(BACKWARD, MICROSTEP);
  } else {
    myStepper1->onestep(BACKWARD, DOUBLE);
  }
}
void backwardstep1() {  
  if (DIRECTION > 0) {  
    myStepper1->onestep(FORWARD, DOUBLE);
  } else {
    myStepper1->onestep(FORWARD, MICROSTEP);
  }
}

AccelStepper Astepper1(forwardstep1, backwardstep1); // use functions to step

boolean reset_started = false;
inline void reset_lp() {
    if (!reset_started) {
      Serial.println("Set reset speed.");
      Astepper1.setSpeed(DIRECTION*MICROSTEPS*450);
      reset_started = true;
    }
    Astepper1.runSpeed();
}

inline void reset_done() {
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
}

#endif

#if STEPPER_DRIVER == 1

AccelStepper Astepper1(1, 9, 8);
#define MICROSTEPS 8

boolean reset_started = false;
inline void reset_lp() {
  if (!reset_started) {
    reset_started = true;
    if (DIRECTION > 0) {
      digitalWrite(8, HIGH);
    }
  }
  digitalWrite(9, HIGH);
  delayMicroseconds(150);
  digitalWrite(9, LOW);
  delayMicroseconds(150);
}

inline void reset_done() {
  digitalWrite(8, LOW);
}

#endif


#if STEPPER_DRIVER == 2

#include <AFMotor.h>
AF_Stepper myStepper1(STEPS_PER_ROTATION, 1);
// you can change these to DOUBLE or INTERLEAVE or MICROSTEP!
void forwardstep1() {
  if (DIRECTION > 0) {  
    myStepper1.onestep(BACKWARD, MICROSTEP);
  } else {
    myStepper1.onestep(BACKWARD, DOUBLE);
  }
}
void backwardstep1() {  
  if (DIRECTION > 0) {  
    myStepper1.onestep(FORWARD, DOUBLE);
  } else {
    myStepper1.onestep(FORWARD, MICROSTEP);
  }
}

AccelStepper Astepper1(forwardstep1, backwardstep1); // use functions to step

boolean reset_started = false;
inline void reset_lp() {
    if (!reset_started) {
      Serial.println("Set reset speed.");
      Astepper1.setSpeed(DIRECTION*MICROSTEPS*450);
      reset_started = true;
    }
    Astepper1.runSpeed();
}

inline void reset_done() {
  Astepper1.setSpeed(0);
  Astepper1.runSpeed();
}

#endif

#if STEPPER_DRIVER == 3

AccelStepper Astepper1(1, 9, 8);
#define MICROSTEPS 16

boolean reset_started = false;
inline void reset_lp() {
  if (!reset_started) {
    reset_started = true;
    if (DIRECTION > 0) {
      digitalWrite(8, LOW);
    } else {
      digitalWrite(8, HIGH);
    }
  }
  digitalWrite(9, HIGH);
  delayMicroseconds(75);
  digitalWrite(9, LOW);
  delayMicroseconds(75);
}

inline void reset_done() {
  digitalWrite(8, LOW);
}

#endif



#endif
