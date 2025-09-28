#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Virtual environment name
VENV_NAME="venv"

echo -e "${GREEN}=== Self-Replicating Factory Simulation Runner ===${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_NAME" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating '$VENV_NAME'...${NC}"
    python3 -m venv $VENV_NAME
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully${NC}"
else
    echo -e "${GREEN}Virtual environment '$VENV_NAME' found${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source $VENV_NAME/bin/activate

# Check if matplotlib is installed (needed for analysis visualization)
python -c "import matplotlib" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing matplotlib for visualization...${NC}"
    pip install matplotlib --quiet
    if [ $? -ne 0 ]; then
        echo -e "${RED}Warning: Could not install matplotlib. Visualization will be skipped.${NC}"
    else
        echo -e "${GREEN}matplotlib installed successfully${NC}"
    fi
else
    echo -e "${GREEN}matplotlib is already installed${NC}"
fi

echo ""
echo -e "${YELLOW}Starting factory simulation...${NC}"
echo -e "${YELLOW}This may take a few minutes depending on configuration...${NC}"
echo ""

# Run the main simulation
python3 self_replicating_factory_sim.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Simulation failed to run${NC}"
    deactivate
    exit 1
fi

echo ""
echo -e "${GREEN}Simulation completed successfully!${NC}"
echo ""

# Check if simulation log was created
if [ ! -f "factory_simulation_log.json" ]; then
    echo -e "${RED}Simulation log file not found${NC}"
    deactivate
    exit 1
fi

echo -e "${YELLOW}Running analysis with detailed visualizations...${NC}"
python3 analyze_factory_sim.py

if [ $? -ne 0 ]; then
    echo -e "${RED}Analysis failed to run${NC}"
    deactivate
    exit 1
fi

echo ""
echo -e "${YELLOW}Generating system architecture diagrams...${NC}"
python3 visualize_factory_system.py

if [ $? -ne 0 ]; then
    echo -e "${RED}System visualization failed${NC}"
    # Non-fatal error - continue
fi

echo ""
echo -e "${GREEN}=== Complete! ===${NC}"
echo ""
echo "Output files generated:"
echo "  - factory_simulation_log.json (detailed simulation data)"

# Check which visualization files were created
if [ -f "factory_simulation_analysis_enhanced.png" ]; then
    echo "  - factory_simulation_analysis_enhanced.png (simulation metrics dashboard)"
fi

if [ -f "factory_system_diagram.png" ]; then
    echo "  - factory_system_diagram.png (system architecture diagram)"
fi

if [ -f "factory_production_graph.png" ]; then
    echo "  - factory_production_graph.png (production dependency graph)"
fi

# Try to open visualizations if on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    if [ -f "factory_simulation_analysis_enhanced.png" ] || [ -f "factory_system_diagram.png" ]; then
        echo ""
        echo -e "${YELLOW}Opening visualizations...${NC}"
        [ -f "factory_simulation_analysis_enhanced.png" ] && open factory_simulation_analysis_enhanced.png 2>/dev/null
        [ -f "factory_system_diagram.png" ] && open factory_system_diagram.png 2>/dev/null
    fi
fi

# Deactivate virtual environment
deactivate

echo ""
echo -e "${GREEN}Virtual environment deactivated${NC}"
echo -e "${GREEN}Done!${NC}"