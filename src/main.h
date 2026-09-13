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

#define DITTO_SAVE_VERSION 1U
typedef struct {
    uint8_t version;
    uint16_t score;
} save_t;

extern uint8_t state;
extern uint16_t run_seed;

#endif
