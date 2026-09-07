# KiCad 9 baseline (tested CLI: 9.0.7). Every public export shares one transaction.
# KICAD_CLI may be a multiword invocation, e.g. flatpak run --command=kicad-cli org.kicad.KiCad.
# Resolution and the actual --version probe belong to manufacturing.py, not command -v.
PYTHON ?= python3
KICAD_CLI ?=
export KICAD_CLI

EXPORT_TARGETS := all package gerbers drills ipc bom cpl zip-gerbers zip-flytest
PRODUCTION_TARGETS := release production
PROTOTYPE_TARGETS := prototype
.DEFAULT_GOAL := all
.PHONY: $(EXPORT_TARGETS) $(PRODUCTION_TARGETS) $(PROTOTYPE_TARGETS) check _manufacturing clean help test

ifneq ($(filter clean,$(MAKECMDGOALS)),)
ifneq ($(filter-out clean,$(MAKECMDGOALS)),)
$(error Run clean separately from other targets)
endif
endif

# The single shared prerequisite runs once even for make -j4 all gerbers drills.
# Direct exports deliberately verify and publish the complete coherent package.
# 'all', 'release', 'production' enforce holds for production file publication.
# 'gerbers' and 'prototype' publish prototype packages when holds are open.
$(EXPORT_TARGETS) $(PRODUCTION_TARGETS) $(PROTOTYPE_TARGETS) check: _manufacturing

_MODE := $(if $(filter $(PRODUCTION_TARGETS) all,$(or $(MAKECMDGOALS),all)),build,\
         $(if $(filter $(PROTOTYPE_TARGETS) gerbers,$(MAKECMDGOALS)),prototype,\
         $(if $(filter $(EXPORT_TARGETS),$(MAKECMDGOALS)),build,check)))

_manufacturing:
	@$(PYTHON) -B scripts/manufacturing.py $(_MODE)

clean:
	@$(PYTHON) -B scripts/manufacturing.py clean

test:
	@$(PYTHON) -B -m unittest discover -s tests -v

help:
	@$(PYTHON) -B scripts/manufacturing.py --help
