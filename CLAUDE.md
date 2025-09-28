# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ultra-realistic self-replicating solar factory simulation with 250+ components, 16 specialized module types, and sophisticated systems for chemical processing, precision manufacturing, material transport, software production, waste management, and environmental control. The simulation reveals that true autonomous replication requires 800-1200 days and 2-3x more resources than simplified models suggest.

**NEW: Fully Modular Architecture** - The system now features a complete modular framework where subsystems can be easily swapped, parallelized, and reconfigured without modifying core code. See MODULAR_GUIDE.md for details.

## Key Commands

### Running the Simulation

**Traditional Mode:**
```bash
# Quick automated run (handles venv, runs simulation, analysis & visualization)
./run_simulation.sh  # Runs complete pipeline

# Or run manually:
python3 self_replicating_factory_sim.py  # Runs with CONFIG settings
```

**Modular Mode (NEW):**
```python
# Run with modular architecture
from modular_factory_adapter import ModularFactory
factory = ModularFactory()
factory.run_simulation(max_hours=1000)

# Or use custom subsystems
from custom_subsystems import GeneticRoutingTransport
factory.add_custom_subsystem("transport", GeneticRoutingTransport())
```

**Analysis & Visualization:**
```bash
# Analyze results after simulation completes
python3 analyze_factory_sim.py           # Enhanced 12-panel dashboard

# Generate system architecture diagrams
python3 visualize_factory_system.py      # Creates flow diagrams

# View simulation output
cat factory_simulation_log.json | python3 -m json.tool | head -100
```

### Dependencies
- Python 3.x (no external dependencies for main simulation)
- Optional: `matplotlib` for visualization in analyze_factory_sim.py
  ```bash
  pip3 install matplotlib  # Only if visualization needed
  ```

## Spec System (NEW)

The Factory Specification (spec) system allows you to define complete factory configurations in external files, enabling easy experimentation with different factory designs without modifying code. This system provides a declarative way to configure resources, recipes, modules, and constraints using YAML, JSON, or custom `.spec` format files.

### Spec System Architecture

The spec system is built around several key components:

- **`spec_loader.py`**: Core module providing spec loading, validation, and integration capabilities
- **`SPEC_FORMAT.md`**: Complete documentation of spec file format and syntax
- **`specs/` directory**: Contains predefined spec files for different factory configurations
- **Command-line integration**: Native support for spec files via `--spec` argument

### Available Spec Files

The simulation comes with these predefined specifications:

- **`specs/default.spec`**: Ultra-realistic factory with 250+ components and 16 specialized modules
  - Complete component hierarchy from raw materials to finished products
  - Realistic chemical processing, electronics manufacturing, and assembly chains
  - Full constraint modeling (energy, thermal, contamination, quality control)

- **`specs/minimal.spec`**: Simplified factory with ~50 essential components
  - Streamlined for faster simulation and testing
  - Core production chains without complex dependencies
  - Ideal for development and prototyping

- **`specs/minimal.json`**: JSON version of minimal spec
  - Alternative format for JSON-based tooling
  - Identical functionality to minimal.spec

### Running with Specs

**Command Line Usage:**
```bash
# Use default built-in configuration (no spec)
python3 self_replicating_factory_sim.py

# Use minimal spec for faster simulation
python3 self_replicating_factory_sim.py --spec specs/minimal.spec

# Use full realistic spec
python3 self_replicating_factory_sim.py --spec specs/default.spec

# Use spec with specific profile
python3 self_replicating_factory_sim.py --spec specs/default.spec --profile high_throughput

# Custom parameters with spec
python3 self_replicating_factory_sim.py --spec specs/minimal.spec --max-hours 5000 --output custom_results.json
```

**Programmatic Usage:**
```python
from spec_loader import load_factory_spec

# Load complete factory configuration from spec
ResourceType, recipes, module_specs, config = load_factory_spec("specs/minimal.spec")

# Create factory with spec-defined configuration
factory = Factory(config)
factory.recipes = recipes
factory.module_specs = module_specs
```

### Spec Loader Module Capabilities

The `spec_loader.py` module provides comprehensive spec management:

**SpecLoader Class:**
- **`load_spec(path)`**: Load and validate spec files with inheritance support
- **`create_resource_enum()`**: Generate ResourceType enum from spec resources
- **`create_recipes()`**: Convert spec recipes to Recipe objects
- **`create_module_specs()`**: Generate ModuleSpec objects from spec modules
- **`create_config()`**: Build CONFIG dictionary with profile support

**SpecRegistry Class:**
- **`list_specs()`**: Discover available spec files
- **`load(name)`**: Load spec by name from registry
- **`get_description(name)`**: Get spec metadata without full loading

**SpecValidator Class:**
- **Dependency validation**: Ensures all recipe inputs/outputs exist
- **Cycle detection**: Prevents circular dependencies in recipes
- **Module validation**: Verifies module specifications are valid
- **Resource validation**: Checks resource definitions for completeness

**Key Features:**
- **Inheritance**: Specs can inherit from parent specs with `parent` metadata field
- **External recipe files**: Large recipe sets can be stored in separate files
- **Profile support**: Multiple configuration variants within single spec
- **Format flexibility**: Supports YAML (.spec, .yaml), JSON (.json)
- **Validation**: Comprehensive validation prevents invalid configurations
- **Dynamic enums**: ResourceType enum generated dynamically from spec

### Spec Format Documentation

The complete specification format is documented in `SPEC_FORMAT.md`, including:

**Core Sections:**
- **Metadata**: Name, version, description, inheritance
- **Resources**: Material properties (density, temperature, contamination sensitivity)
- **Recipes**: Production chains with inputs, outputs, energy, time requirements
- **Modules**: Production module specifications (throughput, power, reliability)
- **Initial State**: Starting modules, resources, and energy systems
- **Constraints**: Global factory parameters and feature toggles
- **Subsystems**: Individual subsystem configurations
- **Profiles**: Configuration variations (high_throughput, energy_efficient, etc.)

**Advanced Features:**
- **Inheritance**: Child specs override parent values
- **Recipe files**: External recipe definitions for modularity
- **Dynamic validation**: Real-time dependency and cycle checking
- **Profile switching**: Runtime configuration variants

**Example Spec Structure:**
```yaml
metadata:
  name: "Custom Factory"
  version: "1.0.0"
  description: "Specialized factory configuration"

resources:
  STEEL:
    density: 7.8
    contamination_sensitivity: 0.1

recipes:
  - output: STEEL_BEAM
    inputs:
      STEEL: 10
    energy_kwh: 50
    time_hours: 2.0
    required_module: cnc

modules:
  cnc:
    max_throughput: 20.0
    power_consumption_active: 50.0

constraints:
  parallel_processing_limit: 10
  enable_degradation: true

profiles:
  fast_mode:
    processing_speed_multiplier: 2.0
```

### Integration Benefits

The spec system provides significant advantages:

1. **No Code Changes**: Define arbitrary factory configurations without modifying simulation code
2. **Experimentation**: Easy A/B testing of different factory designs
3. **Validation**: Automatic validation prevents invalid configurations
4. **Modularity**: Reusable components through inheritance and external files
5. **Performance**: Minimal vs. realistic configurations for different use cases
6. **Documentation**: Self-documenting factory configurations with metadata

## Modular Architecture (NEW)

The simulation now features a fully modular architecture with these components:

### Core Modular Files
- **`modular_framework.py`**: Base interfaces, event bus, orchestrator, configuration management
- **`modular_factory_adapter.py`**: Wrappers for existing subsystems, modular factory implementation
- **`custom_subsystems.py`**: Example advanced subsystems (genetic routing, swarm transport, predictive maintenance)
- **`configs/modular_base.json`**: Hierarchical configuration with profiles
- **`MODULAR_GUIDE.md`**: Complete documentation for the modular system

### Key Features
- **Event-Driven Communication**: Subsystems communicate via publish/subscribe events
- **Dependency Injection**: All subsystems use constructor injection
- **Parallel Execution**: Independent subsystems can run concurrently
- **Hot-Swappable**: Replace subsystems at runtime
- **Configuration Profiles**: Switch between high_throughput, energy_efficient, high_quality modes
- **Testing Support**: Mock subsystems and event recording

### Example Usage
```python
from modular_framework import SubsystemOrchestrator, UpdateStrategy
from modular_factory_adapter import ModularFactory
from custom_subsystems import SmartGridEnergySystem

# Create modular factory
factory = ModularFactory()

# Add custom subsystem
smart_grid = SmartGridEnergySystem()
factory.add_custom_subsystem("smart_grid", smart_grid)

# Enable parallel execution
factory.set_update_strategy(UpdateStrategy.PARALLEL)

# Run simulation
result = factory.run_simulation(max_hours=1000)
```

## Traditional Architecture & Key Concepts

### Component Hierarchy (250+ Components)
The simulation models manufacturing complexity through:
- **Raw Materials**: 7 types of ores
- **Chemical Products**: 10+ acids, solvents, polymers
- **Refined Materials**: Metals, glass, plastics
- **Components**: 40+ electronic, 30+ mechanical, 15+ sensors
- **Software**: PLC programs, firmware, AI models
- **16 Factory Modules**: Mining, Chemical, CNC, Cleanroom, Transport, etc.

Each component has realistic recipes with tolerances, contamination requirements, and software dependencies.

### Core Classes and Data Structures

- **ResourceType (Enum)**: 250+ component types
- **Recipe**: Production requirements with tolerances, cleanroom class, software needs, waste products
- **Task**: Production job with transport, quality yield, contamination impact
- **Factory**: Main engine with 15+ subsystems
- **TransportSystem**: AGV fleet management and routing
- **WasteStream**: Recycling with 60-95% recovery rates
- **SoftwareProductionSystem**: Version control and bug tracking
- **CleanRoomEnvironment**: Contamination and yield modeling
- **ThermalManagementSystem**: Heat generation and cooling
- **ModuleState**: Degradation, maintenance, efficiency tracking

### Critical Algorithms

1. **Dependency Resolution**: The factory uses topological sorting to determine which components must be produced before others. See `_calculate_requirements()` method. Dependencies automatically get `priority + 1` to ensure proper ordering.

2. **Task Scheduling**: Priority queue (heapq) manages task execution order based on dependencies and resource availability. Tasks blocked by constraints are tracked separately.

3. **Energy Management**:
   - Solar generation: `capacity_kw * 8/24 * duration_hours` (assumes 8 peak sun hours daily)
   - Battery efficiency: 95% discharge efficiency, always maintains 20% reserve
   - Energy availability: Solar generation + usable battery storage

4. **Parallel Processing**: Modules can handle multiple tasks simultaneously up to `parallel_processing_limit`.

5. **Production Time Calculation**:
   - Base time: `recipe.time_hours * quantity`
   - With parallelization: `time / min(available_modules, parallel_limit)`
   - With learning: `time * learning_factor^(completed_similar_tasks/10)`
   - Learning improves efficiency by 5% per 10 similar tasks

### Constraint Systems

The ultra-realistic simulation models:
- **Resource constraints**: Material availability with storage limits (volume/weight)
- **Energy constraints**: Solar angle calculations, weather, battery degradation
- **Module constraints**: Throughput, degradation, maintenance, failures
- **Transport constraints**: AGV routing, battery management, congestion
- **Thermal constraints**: Heat generation, cooling capacity (COP-based)
- **Contamination constraints**: Cleanroom classes, particle counts, yield impact
- **Software constraints**: Development time, bug rates, version compatibility
- **Quality constraints**: Defect rates, rework, tolerance stack-up

### Output Files

- `factory_simulation_log.json`: Complete simulation data including:
  - Configuration parameters
  - Material requirements
  - Task completion history
  - Log entries with timestamps
  - Metrics time series
  - Final status

- `factory_simulation_analysis.png`: 9-panel dashboard showing:
  - Task status evolution over time
  - Module production progress
  - Resource distribution
  - Bottleneck analysis
  - Production milestones
  - Efficiency metrics

- `factory_system_diagram.png`: System architecture visualization showing:
  - Material flow hierarchy (7 levels)
  - Module production network
  - Energy flow (solar/battery)
  - Module interdependencies

- `factory_production_graph.png`: Detailed production dependency graph showing:
  - All component relationships
  - Production paths
  - Level-based organization

## Visualization Module

The `visualize_factory_system.py` module generates comprehensive diagrams showing the factory's structure and material flow:

### Key Components
- **FactoryVisualizer class**: Main visualization engine
- **ResourceType enum**: Mirrors main simulation's component types
- **Hierarchical layout**: 7-level production hierarchy visualization
- **Module network**: Shows inter-module dependencies

### Visualization Types
1. **Material Flow Hierarchy**: Shows progression from raw materials to complete factory
2. **Module Production Network**: Displays module interactions and energy flows
3. **Production Dependency Graph**: Detailed component relationships

### Integration
The visualization module:
- Reads from `factory_simulation_log.json` for context
- Works independently if log file is missing
- Called automatically by `run_simulation.sh`
- Generates multiple PNG output files

### Updating Visualizations
When adding new components to the simulation:
1. Add to `ResourceType` enum in `visualize_factory_system.py`
2. Update `resource_levels` dict with appropriate level (0-6)
3. Add dependencies to `load_recipes()` method
4. Update color schemes if needed in `level_colors` or `module_colors`

## Modification Guidelines

### Adding New Components
1. Add to `ResourceType` enum in `self_replicating_factory_sim.py`
2. Create `Recipe` with inputs, energy, time, and module requirements
3. Ensure dependency chain is complete (all inputs must be producible)

### Tuning Performance
Adjust `CONFIG` parameters:
- **Realism toggles** (set to False for idealized simulation):
  - `enable_capacity_limits`: Module throughput constraints
  - `enable_degradation`: Equipment wear and failures
  - `enable_quality_control`: Production defects and yields
  - `enable_weather`: Realistic solar generation
  - `enable_maintenance`: Required maintenance downtime
  - `enable_storage_limits`: Physical storage constraints
  - `enable_batch_processing`: Min/max batch sizes
- **Performance parameters**:
  - `parallel_processing_limit`: Max concurrent tasks per module
  - `solar_panel_efficiency`: Solar conversion efficiency
  - `*_speed_multiplier`: Speed up specific module types
  - `learning_curve_factor`: Learning improvement rate

### Analyzing Bottlenecks
The simulation tracks blocking events. Check `factory_simulation_log.json`:
- Search for "blocked" in log_entries
- Review bottleneck categories in analysis output
- Identify critical path components

## Common Patterns

### Running Optimization Loops
```python
# Modify CONFIG parameters
# Run simulation
# Parse factory_simulation_log.json
# Evaluate metrics (replication_time, resource_efficiency)
# Iterate with new parameters
```

### Extracting Specific Metrics
```python
import json
with open("factory_simulation_log.json") as f:
    data = json.load(f)

# Access time series metrics
metrics = data["metrics"]
# Access completed tasks
completed = data["completed_tasks"]
# Access bottleneck events
blocked = [e for e in data["log_entries"] if "blocked" in e["message"]]
```

## Future Work: Dynamic Subsystems

A comprehensive plan exists in `DYNAMIC_SUBSYSTEMS_PLAN.md` to make all subsystems fully dynamic, eliminating hardcoded ResourceType references. This will enable:
- Complete flexibility in defining custom resource sets
- Subsystem configurations in spec files
- Better maintainability and testing
- Full backward compatibility

The plan involves creating dynamic wrapper classes, updating the spec format, and implementing a subsystem factory pattern.

## Important Implementation Details

### Task States (5 possible states)
- `queued`: Ready to process
- `active`: Currently producing
- `completed`: Finished successfully
- `blocked`: Waiting for dependencies
  - `blocked_module`: Missing required production module
  - `blocked_resources`: Insufficient input materials
  - `blocked_energy`: Insufficient power

### Module Bootstrap
- Factory initializes with exactly 1 of each basic module type
- Completed tasks ending in "_MODULE" automatically increase module count
- Critical for breaking circular dependencies (modules need components that require modules)

### Simulation Timing
- **Time step**: 0.1 hour increments for precision
- **Max duration**: 10,000 hours hard limit
- **Termination**: All factory module tasks must reach "completed" status
- **Metrics collection**: Every 1.0 hour for analysis

### Key Implementation Choices
- **Task Priority**: Lower priority numbers execute first (heapq min-heap)
- **Task IDs**: Format `task_{counter:05d}_{output.value}` for uniqueness
- **Module Production**: Each module type increases corresponding processing capacity
- **Learning Effects**: Based on exact recipe match, compounds over time
- **Energy Storage**: Battery acts as buffer for continuous 24-hour operation
- **Material Buffer**: Small inventories prevent cascading delays
- **No recycling**: Completed products cannot be broken down
- **Log limits**: Keeps last 1000 log entries and 100 completed tasks to manage memory

## Modular Architecture Implementation Details

### Subsystem Lifecycle
1. **Registration**: `orchestrator.register_subsystem(name, subsystem, deps)`
2. **Initialization**: `subsystem.initialize(config, event_bus)`
3. **Update Loop**: `subsystem.update(delta_time, context)`
4. **Event Processing**: `event_bus.process_events()`
5. **Metrics Collection**: `subsystem.get_metrics()`
6. **State Management**: `get_state()` / `set_state()`
7. **Shutdown**: `subsystem.shutdown()`

### Event Types and Patterns
```python
# Core event types in modular_framework.py
EventType.RESOURCE_PRODUCED    # Resource creation
EventType.RESOURCE_CONSUMED    # Resource usage
EventType.MODULE_CREATED        # New module online
EventType.MODULE_FAILED         # Module failure
EventType.TASK_STARTED         # Task beginning
EventType.TASK_COMPLETED       # Task finished
EventType.TRANSPORT_REQUESTED  # Transport needed
EventType.ENERGY_AVAILABLE    # Power status
EventType.THERMAL_LIMIT_REACHED  # Heat warning
```

### Dependency Injection Pattern
```python
# SubsystemContainer manages dependencies
container = SubsystemContainer()
container.bind_class("transport", TransportSystemWrapper)
container.bind("energy", lambda: SmartGridEnergySystem(), singleton=True)

# Resolve all dependencies
subsystems = container.resolve_all()
```

### Update Strategy Implementation
- **SEQUENTIAL**: Topological sort based on dependencies
- **PARALLEL**: Groups by dependency level, ThreadPoolExecutor
- **PRIORITY**: User-defined priority ordering
- **DEPENDENCY**: Strict dependency resolution order

### Configuration Hierarchy
```
configs/modular_base.json (base)
    ↓ merge
subsystem-specific configs
    ↓ override
profile configs (high_throughput, etc)
    ↓ override
runtime modifications
```

### Wrapper Implementation Pattern
```python
class SubsystemWrapper(SubsystemBase):
    def __init__(self):
        self.legacy_system = None

    def initialize(self, config, event_bus):
        # Create legacy with extracted config
        self.legacy_system = LegacySystem(config.config)
        # Subscribe to events
        event_bus.subscribe(EventType.X, self.handle_event)

    def update(self, delta_time, context):
        # Adapt context to legacy format
        result = self.legacy_system.process(...)
        # Publish events for changes
        self.publish_event(EventType.Y, result)
        return adapted_result
```

## Potential Gotchas and Edge Cases

### Modular System Gotchas
- **Event Ordering**: Events process after all subsystem updates
- **Context Copying**: Each parallel subsystem gets context copy (memory overhead)
- **Config Merging**: Later configs override earlier ones completely
- **Singleton Subsystems**: Shared state across all references
- **Event Bus Queue**: Unbounded queue can grow with many events

### Traditional System Gotchas

#### Recursive Requirement Calculation
- `calculate_replication_requirements()` recursively traverses ALL sub-component dependencies
- Quantities scale multiplicatively through dependency chain
- **Warning**: No cycle detection in dependency graph (could cause infinite loops if cycles exist)

#### Resource Precision
- Uses `defaultdict(float)` allowing fractional quantities
- Production ratios: `input_qty * quantity / recipe.output_quantity`
- May accumulate rounding errors in deep dependency chains

#### Blocking Resolution
- Pull-based strategy: `check_blocked_tasks()` polls for unblocking conditions
- Dependencies tracked by task IDs in `blocked_by` sets
- Module availability checked each simulation step

## Testing & Validation

Run quick validation:
```bash
python3 -c "from self_replicating_factory_sim import Factory, CONFIG; f = Factory(CONFIG); print('Factory initialized successfully')"
```

Check simulation consistency:
- Total energy consumed should match generation + initial battery
- All completed tasks should have had required resources
- Module counts should match production records
- No dependency cycles in recipe graph