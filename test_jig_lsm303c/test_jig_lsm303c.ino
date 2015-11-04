// Requires Sparkfun LSM303C Arduino library:
//   https://github.com/sparkfun/SparkFun_LSM303C_6_DOF_IMU_Breakout_Arduino_Library

// I2C interface by default
//
#include "Wire.h"
#include "SparkFunIMU.h"
#include "SparkFunLSM303C.h"
#include "LSM303CTypes.h"

/*
 * define DEBUG 1 in SparkFunLSM303C.cpp turns on debugging statements.
 * Redefine to 0 to turn them off.
 */

/*
 * SPI pins defined in SparkFunLSM303C.h for Pro Mini
 * D10 -> SDI/SDO
 * D11 -> SCLK
 * D12 -> CS_XL
 * D13 -> CS_MAG
 */

LSM303C myIMU;

void setup() {
  Serial.begin(115200);

  if (myIMU.begin(
                ///// Interface mode options
                  //MODE_SPI,
                  MODE_I2C,

                ///// Magnetometer output data rate options
                  //MAG_DO_0_625_Hz,
                  //MAG_DO_1_25_Hz,
                  //MAG_DO_2_5_Hz,
                  //MAG_DO_5_Hz,
                  //MAG_DO_10_Hz,
                  //MAG_DO_20_Hz,
                  MAG_DO_40_Hz,
                  //MAG_DO_80_Hz,

                ///// Magnetic field full scale options
                  //MAG_FS_4_Ga,
                  //MAG_FS_8_Ga,
                  //MAG_FS_12_Ga,
                  MAG_FS_16_Ga,
                  
                ///// Magnetometer block data updating options
                  //MAG_BDU_DISABLE,
                  MAG_BDU_ENABLE,

                ///// Magnetometer X/Y axes ouput data rate
                  //MAG_OMXY_LOW_POWER,
                  //MAG_OMXY_MEDIUM_PERFORMANCE,
                  MAG_OMXY_HIGH_PERFORMANCE,
                  //MAG_OMXY_ULTRA_HIGH_PERFORMANCE,

                ///// Magnetometer Z axis ouput data rate
                  //MAG_OMZ_LOW_PW,
                  //MAG_OMZ_MEDIUM_PERFORMANCE,
                  MAG_OMZ_HIGH_PERFORMANCE,
                  //MAG_OMZ_ULTRA_HIGH_PERFORMANCE,

                ///// Magnetometer run mode
                  MAG_MD_CONTINUOUS,
                  //MAG_MD_SINGLE,
                  //MAG_MD_POWER_DOWN_1,
                  //MAG_MD_POWER_DOWN_2,

                ///// Acceleration full scale
                  ACC_FS_2g,
                  //ACC_FS_4g,
                  //ACC_FS_8g,

                ///// Accelerometer block data updating
                  //ACC_BDU_DISABLE,
                  ACC_BDU_ENABLE,

                ///// Enable X, Y, and/or Z axis
                  //ACC_DISABLE_ALL,
                  //ACC_X_ENABLE,
                  //ACC_Y_ENABLE,
                  //ACC_Z_ENABLE,
                  //ACC_X_ENABLE|ACC_Y_ENABLE,
                  //ACC_X_ENABLE|ACC_Z_ENABLE,
                  //ACC_Y_ENABLE|ACC_Z_ENABLE,
                  ACC_X_ENABLE|ACC_Y_ENABLE|ACC_Z_ENABLE,

                ///// Accelerometer output data rate
                  //ACC_ODR_POWER_DOWN
                  //ACC_ODR_10_Hz
                  //ACC_ODR_50_Hz
                  ACC_ODR_100_Hz
                  //ACC_ODR_200_Hz
                  //ACC_ODR_400_Hz
                  //ACC_ODR_800_Hz
                ) != IMU_SUCCESS)
  {
    Serial.println("Failed setup.");
    while(1);
  }
}

float x, y, z;

void loop()
{

  x = myIMU.readAccelX();
  y = myIMU.readAccelY();
  z = myIMU.readAccelZ();

  Serial.print(x);
  Serial.print(",");
  Serial.print(y);
  Serial.print(",");
  Serial.print(z);
  Serial.print("\n");

}
