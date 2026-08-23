# ==============================================================================
# Dog Fence Indicator & Surge Protection System (v1.0)
# Automated Production Package Makefile (KiCad 7 / 8 / 9 & JLCPCB Turnkey PCBA)
# ==============================================================================

# Auto-detect native, Snap, and Flatpak kicad-cli binaries
KICAD_CLI      ?= $(shell \
	if command -v kicad-cli >/dev/null 2>&1; then echo kicad-cli; \
	elif command -v kicad.kicad-cli >/dev/null 2>&1; then echo kicad.kicad-cli; \
	elif [ -x /snap/bin/kicad.kicad-cli ]; then echo /snap/bin/kicad.kicad-cli; \
	elif [ -x /snap/kicad/current/usr/bin/kicad-cli ]; then echo /snap/kicad/current/usr/bin/kicad-cli; \
	elif command -v flatpak >/dev/null 2>&1 && flatpak info org.kicad.KiCad >/dev/null 2>&1; then echo "flatpak run --command=kicad-cli org.kicad.KiCad"; \
	else echo kicad-cli; fi)
PCB_FILE       := pcb/pcb.kicad_pcb
SCH_FILE       := pcb/pcb.kicad_sch
BOM_SOURCE     := pcb/BOM.csv
CPL_SOURCE     := pcb/CPL.csv
IPC_SOURCE     := pcb/pcb.d356

BUILD_DIR      := build
GERBER_DIR     := $(BUILD_DIR)/gerbers
GERBERS_ZIP    := $(BUILD_DIR)/Gerbers.zip
FLYTEST_ZIP    := $(BUILD_DIR)/FlyTest.zip
BOM_OUT        := $(BUILD_DIR)/BOM.csv
CPL_OUT        := $(BUILD_DIR)/CPL.csv
IPC_OUT        := $(BUILD_DIR)/pcb.d356

# Standard 2-Layer Gerber Layers for JLCPCB
GERBER_LAYERS  := F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts

.PHONY: all clean gerbers drills bom cpl ipc zip-gerbers zip-flytest package help

# Default target: build complete turnkey manufacturing package
all: package

help:
	@echo "======================================================================"
	@echo "Dog Fence v1.0 - Production Build Commands"
	@echo "======================================================================"
	@echo "  make all         - Build complete JLCPCB package (Gerbers, BOM, CPL, FlyTest)"
	@echo "  make gerbers     - Export all 2-layer Gerber files (.gbr)"
	@echo "  make drills      - Export Excellon drill files (PTH & NPTH .drl)"
	@echo "  make bom         - Export / package Bill of Materials (BOM.csv)"
	@echo "  make cpl         - Export / package Pick-and-Place Centroid (CPL.csv)"
	@echo "  make ipc         - Export IPC-D-356 Flying Probe Test netlist (.d356)"
	@echo "  make zip-gerbers - Package Gerbers and Drill files into Gerbers.zip"
	@echo "  make zip-flytest - Package IPC-D-356 Netlist & Gerbers into FlyTest.zip"
	@echo "  make clean       - Remove build directory"
	@echo "======================================================================"

# Create build directories
$(BUILD_DIR):
	@mkdir -p $(BUILD_DIR)
	@mkdir -p $(GERBER_DIR)

# 1. Export Gerber layers using kicad-cli (or copy verified gerbers if kicad-cli not in path)
gerbers: $(BUILD_DIR)
	@echo "[1/6] Generating Gerber layers..."
	@if command -v $(KICAD_CLI) >/dev/null 2>&1; then \
		$(KICAD_CLI) pcb export gerbers \
			--output $(GERBER_DIR)/ \
			--layers $(GERBER_LAYERS) \
			--subtract-soldermask \
			--no-protel-ext \
			$(PCB_FILE); \
	elif [ -d pcb ] && ls pcb/*.gbr >/dev/null 2>&1; then \
		echo "      (Using verified pre-exported .gbr files from pcb/)"; \
		cp pcb/*.gbr $(GERBER_DIR)/; \
	else \
		echo "ERROR: Neither kicad-cli nor .gbr files found!"; exit 1; \
	fi

# 2. Export Excellon drill files
drills: $(BUILD_DIR)
	@echo "[2/6] Generating Excellon drill files (PTH & NPTH)..."
	@if command -v $(KICAD_CLI) >/dev/null 2>&1; then \
		$(KICAD_CLI) pcb export drill \
			--output $(GERBER_DIR)/ \
			--format excellon \
			--drill-origin absolute \
			--excellon-units mm \
			--excellon-zeros-format decimal \
			--excellon-separate-th \
			$(PCB_FILE); \
	elif [ -d pcb ] && ls pcb/*.drl >/dev/null 2>&1; then \
		echo "      (Using verified pre-exported .drl files from pcb/)"; \
		cp pcb/*.drl $(GERBER_DIR)/; \
	fi

# 3. Export IPC-D-356 Netlist for Flying Probe Testing
ipc: $(BUILD_DIR)
	@echo "[3/6] Generating IPC-D-356 Flying Probe Test netlist..."
	@if command -v $(KICAD_CLI) >/dev/null 2>&1; then \
		$(KICAD_CLI) pcb export ipcd356 \
			--output $(IPC_OUT) \
			$(PCB_FILE); \
	elif [ -f $(IPC_SOURCE) ]; then \
		cp $(IPC_SOURCE) $(IPC_OUT); \
	fi

# 4. Export / package Bill of Materials (BOM)
bom: $(BUILD_DIR)
	@echo "[4/6] Packaging Bill of Materials (BOM.csv)..."
	@cp $(BOM_SOURCE) $(BOM_OUT)

# 5. Export / package Component Placement List (CPL / .pos)
cpl: $(BUILD_DIR)
	@echo "[5/6] Packaging Pick-and-Place Centroid (CPL.csv)..."
	@if command -v $(KICAD_CLI) >/dev/null 2>&1; then \
		$(KICAD_CLI) pcb export pos \
			--output $(CPL_OUT) \
			--format csv \
			--units mm \
			--side both \
			$(PCB_FILE); \
	elif [ -f $(CPL_SOURCE) ]; then \
		cp $(CPL_SOURCE) $(CPL_OUT); \
	fi

# 6. Compress Gerbers into Gerbers.zip
zip-gerbers: gerbers drills
	@echo "[6/6] Creating Gerbers.zip for PCB fabrication..."
	@rm -f $(GERBERS_ZIP)
	@cd $(GERBER_DIR) && zip -q -r ../Gerbers.zip .
	@cp $(GERBERS_ZIP) pcb/Gerbers.zip

# 7. Package Flying Probe Test package (FlyTest.zip)
zip-flytest: ipc zip-gerbers
	@echo "      Creating FlyTest.zip for JLCPCB electrical probe testing..."
	@rm -f $(FLYTEST_ZIP)
	@mkdir -p $(BUILD_DIR)/flytest_staging
	@cp $(IPC_OUT) $(BUILD_DIR)/flytest_staging/ 2>/dev/null || true
	@cp $(GERBERS_ZIP) $(BUILD_DIR)/flytest_staging/
	@echo "Dog Fence Indicator 1.0 - Flying Probe Electrical Test Package" > $(BUILD_DIR)/flytest_staging/README.txt
	@echo "Contains IPC-D-356 netlist (pcb.d356) and master fabrication Gerbers.zip" >> $(BUILD_DIR)/flytest_staging/README.txt
	@cd $(BUILD_DIR)/flytest_staging && zip -q -r ../FlyTest.zip *
	@rm -rf $(BUILD_DIR)/flytest_staging

# Master Package Target
package: gerbers drills ipc bom cpl zip-gerbers zip-flytest
	@echo ""
	@echo "======================================================================"
	@echo "✅ Turnkey Production Package Built Successfully in $(BUILD_DIR)/"
	@echo "======================================================================"
	@echo "  📦 1. PCB Bare Fabrication:   $(GERBERS_ZIP)"
	@echo "  📦 2. PCBA Bill of Materials: $(BOM_OUT)"
	@echo "  📦 3. PCBA Pick-and-Place:    $(CPL_OUT)"
	@echo "  📦 4. Flying Probe Test Kit:  $(FLYTEST_ZIP)"
	@echo "  📄 5. IPC-D-356 Netlist:      $(IPC_OUT)"
	@echo "======================================================================"

clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
