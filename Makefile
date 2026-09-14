ROM := ditto
EXAMPLES := menus scroll save audio
ENGINE_MK ?= engine/engine.mk
include $(ENGINE_MK)

# Each example builds a standalone ROM that shares src/*.c (audio, debug
# helpers) and the same public Pallet interface as the default ROM.
.PHONY: local examples $(EXAMPLES:%=example-%)
local:
	$(MAKE) ENGINE_MK=../pallet/engine.mk

examples: $(EXAMPLES:%=example-%)

$(EXAMPLES:%=example-%): example-%:
	$(MAKE) --no-print-directory ROM=ditto-$* BUILD=$(BUILD) \
		GAME_SOURCES="src/audio.c src/debug_math.c examples/$*/main.c" \
		LCCFLAGS="$(LCCFLAGS) -Isrc" $(BUILD)/ditto-$*.gb

.PHONY: test
test: all examples
	@for rom in ditto $(EXAMPLES:%=ditto-%); do \
		echo "== pytest: $$rom =="; \
		ROM_NAME=$$rom uv run --project tests pytest tests || exit 1; \
	done
