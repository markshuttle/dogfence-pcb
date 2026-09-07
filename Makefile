# KiCad 9 baseline (tested CLI: 9.0.7). Every public export shares one transaction.
# KICAD_CLI may be a multiword invocation, e.g. flatpak run --command=kicad-cli org.kicad.KiCad.
# Resolution and the actual --version probe belong to manufacturing.py, not command -v.
PYTHON ?= python3
KICAD_CLI ?=
export KICAD_CLI

EXPORT_TARGETS := all package gerbers drills ipc bom cpl zip-gerbers zip-flytest
.DEFAULT_GOAL := all
.PHONY: $(EXPORT_TARGETS) check _manufacturing clean help test

ifneq ($(filter clean,$(MAKECMDGOALS)),)
ifneq ($(filter-out clean,$(MAKECMDGOALS)),)
$(error Run clean separately from other targets)
endif
endif

# The single shared prerequisite runs once even for make -j4 all gerbers drills.
# Direct exports deliberately verify and publish the complete coherent package.
$(EXPORT_TARGETS) check: _manufacturing

_manufacturing:
	@$(PYTHON) -B scripts/manufacturing.py $(if $(filter $(EXPORT_TARGETS),$(or $(MAKECMDGOALS),all)),build,check)

clean:
	@$(PYTHON) -B scripts/manufacturing.py clean

test:
	@$(PYTHON) -B -m unittest discover -s tests -v

help:
	@$(PYTHON) -B scripts/manufacturing.py --help
