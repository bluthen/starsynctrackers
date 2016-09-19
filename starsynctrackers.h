#ifndef __STARSYNCTRACKERS_H
#define __STARSYNCTRACKERS_H

#include <stdint.h>


/** 
 * Structure that holds EEPROM values. The default values are in starsynctrackers.ino
 */
struct SSTVARS {
  float stepsPerRotation;
  float threadsPerInch;
  float r_i;
  float d_s;
  float d_f;
  float recalcIntervalS;
  float endLengthReset;
  float dir;
};

/**
 * Holds the firmware version.
 */
extern const char* sstversion;

/**
 * Holds values from EEPROM.
 */
extern SSTVARS sstvars;

extern float time_diff_s;
extern int sst_reset_count;
extern boolean reset_started;
extern float sst_rate;
extern unsigned long time_solar_start_ms;
extern float time_adjust_s;

/**
 * Runs when true.
 */
extern boolean keep_running;

/**
 * Calculates theta based on running time in seconds.
 * @param time_solar_s Time is seconds.
 * @return The angle the tracker should be at at a certain time.
 */
float sst_theta(float time_solar_s);

/**
 * Given an angle gives you the length on the rod the 
 * trackers should be extended.
 * @param theta The angle at which you would like to know the rod length at.
 * @return Rod length.
 */
float sst_rod_length_by_angle(float theta);

/**
 * Inverse of tracker_calc_steps, gives you time given tracker steps.
 * @param current_steps The number of steps to use to calculate time.
 * @return time in seconds.
 */
float steps_to_time_solar(float current_steps);

/**
 * Gives you time tracker would need to run to be at rod length.
 * @param d rod length
 * @return time in seconds.
 */
float rod_length_to_solar(float d);

/**
 * Saves eeprom values with the contents of sstvars.
 */
void sst_save_sstvars(void);

/** 
 * Resets the tracker to initial position.
 */
void sst_reset(void);

#endif
