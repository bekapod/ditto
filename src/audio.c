#include "audio.h"
#include "sfx.h"

static const sfx_row_t test_sfx_rows[] = {
    {0, SFX_REG_PULSE2_DUTY, DUTY_12_5},
    {0, SFX_REG_PULSE2_ENV, ENV(12, 2)},
    {0, SFX_REG_PULSE2_FREQ_LO, PITCH_LO(1200)},
    {6, SFX_REG_PULSE2_FREQ_HI, PITCH_HI(1200) | SFX_TRIGGER},
    {SFX_END, 0, 0},
};

static const sfx_script_t test_sfx = {
    .rows = test_sfx_rows,
    .channel = SFX_CHANNEL_2,
};

void audio_play_test_sfx(void) {
    sfx_play(&test_sfx);
}
