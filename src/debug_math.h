#ifndef DITTO_DEBUG_MATH_H
#define DITTO_DEBUG_MATH_H

#include <stdint.h>

extern volatile int16_t debug_fx_cases[];
extern volatile uint8_t debug_hit_cases[];

void debug_math_cases(void);

#endif
