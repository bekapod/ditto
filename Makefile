ROM := ditto
ENGINE_MK ?= engine/engine.mk
include $(ENGINE_MK)

.PHONY: local
local:
	$(MAKE) ENGINE_MK=../pallet/engine.mk
