#ifndef __SST_CONSOLE_H
#define __SST_CONSOLE_H

#include "SerialCommand.h"

/**
 * Initialize console.
 */
void sst_console_init(void);

/**
 * Try reading from serial and see if there is anything in the
 * buffer. Processes command if valid.
 */
void sst_console_read_serial(void);

#endif
