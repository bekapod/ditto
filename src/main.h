#ifndef DITTO_MAIN_H
#define DITTO_MAIN_H

#include <stdint.h>

enum {
    STATE_TITLE_INIT,
    STATE_TITLE,
    STATE_PLAY_INIT,
    STATE_PLAY_FADE_IN,
    STATE_PLAY
};

extern uint8_t state;

#endif
