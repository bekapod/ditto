#include <stdint.h>

#include "debug_math.h"
#include "pallet.h"

volatile int16_t debug_fx_cases[10];
volatile uint8_t debug_hit_cases[5];

void debug_math_cases(void) {
    debug_fx_cases[0] = FX(-2);
    debug_fx_cases[1] = FX_INT(FX(-2));
    debug_fx_cases[2] = FX_FRAC(FX(-2) + 0x80);
    debug_fx_cases[3] = FX_MUL_U8(FX(2), 128);
    debug_fx_cases[4] = FX_SIGN(-1);
    debug_fx_cases[5] = FX_SIGN(0);
    debug_fx_cases[6] = FX_SIGN(1);
    debug_fx_cases[7] = FX_CLAMP(FX(-2), FX(-1), FX(1));
    debug_fx_cases[8] = FX_CLAMP(FX(0), FX(-1), FX(1));
    debug_fx_cases[9] = FX_CLAMP(FX(2), FX(-1), FX(1));

    {
        static const hitbox_t a = {0, 0, 10, 10};
        static const hitbox_t miss = {10, 0, 10, 10};
        static const hitbox_t overlap = {9, 0, 10, 10};
        static const hitbox_t far = {20, 0, 10, 10};
        static const hitbox_t box = {10, 20, 8, 8};

        debug_hit_cases[0] = hit_overlaps(a, miss);
        debug_hit_cases[1] = hit_overlaps(a, overlap);
        debug_hit_cases[2] = hit_overlaps(a, far);
        debug_hit_cases[3] = hit_contains(box, 10, 20);
        debug_hit_cases[4] = hit_contains(box, 18, 20);
    }
}
