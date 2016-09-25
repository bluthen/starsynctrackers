#ifndef __STEPPER_DRIVERS_H
#define __STEPPER_DRIVERS_H

#include <AccelStepper.h>

//
// Need AccelStepper fork with AFMotor support with library 
//   https://github.com/adafruit/AccelStepper
// If using Adafruit v2 Motorshield requires the Adafruit_Motorshield v2 library 
//   https://github.com/adafruit/Adafruit_Motor_Shield_V2_Library
// if using adafruit motor shield v1 then you need v1 library
//' https://github.com/adafruit/Adafruit-Motor-Shield-library

// STEPPER_DRIVER
// 0 - Adafruit Motorshield V2 https://www.adafruit.com/products/1438
// 1 - Easy Driver https://www.sparkfun.com/products/12779 (http://www.schmalzhaus.com/EasyDriver/index.html)
// 2 - Adafruit Motorshield V1 https://www.adafruit.com/products/81
// 3 - Big Easy Driver https://www.sparkfun.com/products/12859 (http://www.schmalzhaus.com/BigEasyDriver/)
#define STEPPER_DRIVER 0

#if STEPPER_DRIVER == 0
  #include <Adafruit_MotorShield.h>
  #include "utility/Adafruit_PWMServoDriver.h"
#endif

#if STEPPER_DRIVER == 1
  #define MICROSTEPS 8
#endif

#if STEPPER_DRIVER == 2
  #include <AFMotor.h>
#endif

#if STEPPER_DRIVER == 3
  #define MICROSTEPS 16
#endif

extern AccelStepper Astepper1;
void stepper_init(void);
void stepper_reset_lp(void);
void stepper_reset_done(void);

#endif
