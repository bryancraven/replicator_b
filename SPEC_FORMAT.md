# Factory Specification Format Documentation

## Overview

The Factory Specification (spec) system allows you to define complete factory configurations in external files, enabling easy experimentation with different factory designs without modifying code. Specs can be written in YAML, JSON, or custom `.spec` format (YAML-based).

## Quick Start

### Running with a Spec

```bash
# Use default configuration (no spec)
python3 self_replicating_factory_sim.py

# Use minimal spec for faster simulation
python3 self_replicating_factory_sim.py --spec specs/minimal.spec

# Use spec with a specific profile
python3 self_replicating_factory_sim.py --spec specs/default.spec --profile high_throughput

# Custom parameters
python3 self_replicating_factory_sim.py --spec specs/minimal.spec --max-hours 5000 --output results.json

# Use modular architecture with spec-defined subsystems (NEW)
python3 self_replicating_factory_sim.py --spec specs/genetic_optimized.json --modular
```

### Available Specs

- **`specs/default.spec`**: Ultra-realistic factory with 250+ components and 16 modules
- **`specs/minimal.spec`**: Simplified factory with ~50 components for faster simulation
- **`specs/genetic_optimized.json`**: Factory using genetic algorithms and ML optimization (modular)
- **`specs/high_reliability.json`**: Factory optimized for maximum uptime and reliability (modular)
- **`specs/energy_focused.json`**: Smart grid integrated factory with renewable optimization (modular)

## Spec File Structure

A spec file contains the following sections:

1. Metadata - Name, version, description, inheritance
2. Resources - Materials, components, products
3. Recipes - Production chains and transformations
4. Modules - Production module specifications
5. Initial State - Starting conditions
6. Constraints - Global factory parameters
7. Subsystems - Subsystem configurations
8. Profiles - Configuration variations
9. Subsystem Implementations (NEW) - Specify which subsystem implementations to use

### 1. Metadata

```yaml
metadata:
  name: "Factory Name"
  version: "1.0.0"
  description: "Description of the factory configuration"
  author: "Author Name"
  parent: "path/to/parent.spec"  # Optional inheritance
```

### 2. Resources

Define all materials, components, and products:

```yaml
resources:
  SILICON_ORE:
    density: 2.3              # tons/m³
    storage_temp: 25          # °C
    contamination_sensitivity: 0.1  # 0-1 scale
    hazardous: false          # Optional
    recyclable: true          # Optional
    volume_per_unit: 0.001    # m³
    description: "Raw silicon ore"
```

### 3. Recipes

Define production chains:

```yaml
recipes:
  - output: PURE_SILICON
    output_quantity: 100
    inputs:
      SILICON_ORE: 500
    energy_kwh: 200
    time_hours: 2.0
    required_module: refining
    parallel_capable: true           # Optional
    tolerance_um: 10                 # Optional (micrometers)
    cleanroom_class: 100             # Optional
    software_required: PLC_PROGRAM   # Optional
    waste_products:                  # Optional
      WASTE_SILICON: 5.0
```

### 4. Modules

Define production module specifications:

```yaml
modules:
  cnc:
    max_throughput: 20.0        # units/hour
    power_consumption_idle: 10.0     # kW
    power_consumption_active: 50.0   # kW
    mtbf_hours: 3000            # Mean time between failures
    maintenance_interval: 100    # hours
    degradation_rate: 0.05      # fraction per 1000 hours
    physical_footprint: 100     # m²
    max_batch_size: 50
    min_batch_size: 1
    setup_time: 1.0            # hours
    quality_base_rate: 0.98    # 0-1
    tolerance_capability: 5.0   # Optional (micrometers)
    cleanroom_capable: false   # Optional
```

### 5. Initial State

Define starting conditions:

```yaml
initial_state:
  modules:
    mining: 1
    refining: 1
    cnc: 1
    assembly: 2
  resources:
    STEEL: 100
    COPPER_WIRE: 50
  energy:
    solar_panels: 10
    battery_charge: 100
```

### 6. Constraints

Global factory parameters:

```yaml
constraints:
  # Energy
  initial_solar_capacity_kw: 100
  solar_panel_efficiency: 0.22
  battery_efficiency: 0.95

  # Processing
  parallel_processing_limit: 10
  processing_speed_multiplier: 1.0

  # Physical
  factory_area_m2: 20000
  max_storage_volume_m3: 15000

  # Features (enable/disable)
  enable_degradation: true
  enable_weather: true
  enable_maintenance: true
```

### 7. Subsystems

Configure individual subsystems:

```yaml
subsystems:
  transport:
    enabled: true
    agv_fleet_size: 10
    conveyor_length_m: 500

  thermal:
    enabled: true
    ambient_temperature: 25
    cooling_capacity_kw: 1000

  storage:
    enabled: true
    max_storage_volume_m3: 15000
```

### 8. Profiles

Define configuration variations:

```yaml
profiles:
  high_throughput:
    description: "Optimized for maximum production"
    parallel_processing_limit: 20
    processing_speed_multiplier: 1.5
    initial_solar_capacity_kw: 500

  energy_efficient:
    description: "Minimized energy consumption"
    processing_speed_multiplier: 0.8
    solar_panel_efficiency: 0.25
```

### 9. Subsystem Implementations (NEW)

Define which subsystem implementations to use for complete behavioral configuration:

```yaml
subsystem_implementations:
  transport: "genetic_routing"        # Genetic algorithm-based routing
  maintenance: "predictive_maintenance"  # ML-based predictive maintenance
  quality: "spc_quality"              # Statistical process control
  energy: "smart_grid"                # Smart grid with demand response
  monitoring: "digital_twin"          # Predictive digital twin simulation
```

Available implementations include:

**Transport Systems:**
- `transport_wrapper` - Default transport system
- `genetic_routing` - Genetic algorithm optimization
- `swarm_transport` - Swarm intelligence coordination
- `adaptive_transport` - Learning-based adaptation

**Maintenance Systems:**
- `predictive_maintenance` - ML-based failure prediction

**Quality Control:**
- `spc_quality` - Statistical process control
- `ml_quality` - Machine learning quality control

**Energy Systems:**
- `energy_wrapper` - Default energy system
- `smart_grid` - Smart grid with demand response
- `renewable_optimizer` - Multi-source renewable optimization

**Monitoring:**
- `digital_twin` - Predictive simulation and optimization

This feature enables complete factory configuration without writing Python code. When using `--modular` flag, the specified subsystems will be instantiated and configured using the corresponding `subsystem_data` section.

### 10. Subsystem Data

Configure the behavior of custom subsystem implementations:

```yaml
subsystem_data:
  transport:
    population_size: 100       # For genetic_routing
    mutation_rate: 0.15
    crossover_rate: 0.7

  maintenance:
    failure_threshold: 0.8     # For predictive_maintenance
    predictive_horizon_hours: 168

  energy:
    grid_connection: true      # For smart_grid
    grid_buy_price: 0.12
    demand_response: true
```

## Advanced Features

### Inheritance

Specs can inherit from parent specs:

```yaml
metadata:
  parent: "templates/base.spec"
```

Child specs override parent values.

### Recipe Files

For large recipe sets, use external files:

```yaml
recipes_file: default_recipes.yaml
```

The referenced file should contain:
```yaml
recipes:
  - output: COMPONENT_1
    # ... recipe details
  - output: COMPONENT_2
    # ... recipe details
```

### Validation

The spec loader validates:
- All recipe inputs/outputs exist in resources
- No circular dependencies in recipes
- Module specifications are valid
- Required modules exist for recipes

### Dynamic Resource Types

Resources defined in specs automatically become available as ResourceType enum values in the simulation.

## Creating Custom Specs

### Step 1: Start with a Template

Copy an existing spec as a starting point:
```bash
cp specs/minimal.spec specs/custom/my_factory.spec
```

### Step 2: Define Resources

List all materials and components your factory will use.

### Step 3: Create Recipe Chains

Define how resources transform into products:
1. Start with raw materials (no inputs)
2. Define refinement processes
3. Add component manufacturing
4. Create assembly recipes
5. Define module production

### Step 4: Configure Modules

Define the capabilities of each production module type.

### Step 5: Set Initial State

Specify starting modules and resources.

### Step 6: Tune Constraints

Adjust parameters for desired simulation behavior.

### Step 7: Test

Run the simulation with your spec:
```bash
python3 self_replicating_factory_sim.py --spec specs/custom/my_factory.spec
```

## Best Practices

1. **Start Small**: Begin with minimal specs and add complexity gradually
2. **Validate Dependencies**: Ensure all recipe inputs can be produced
3. **Balance Energy**: Solar generation should support production needs
4. **Test Profiles**: Create profiles for different optimization goals
5. **Document**: Use descriptions in metadata and resources
6. **Version Control**: Track spec versions for reproducibility

## Example: Semiconductor-Focused Factory

```yaml
metadata:
  name: "Semiconductor Fab"
  version: "1.0.0"
  description: "Optimized for chip production"

resources:
  # Focus on semiconductor materials
  SILICON_ORE:
    contamination_sensitivity: 0.1
  PURE_SILICON:
    contamination_sensitivity: 1.0
  SILICON_WAFER:
    contamination_sensitivity: 1.0
  # ... more semiconductor components

modules:
  cleanroom:
    max_throughput: 200.0  # Higher for semiconductors
    cleanroom_capable: true
    quality_base_rate: 0.999

constraints:
  cleanroom_class: 10  # Class 10 cleanroom
  enable_contamination: true

profiles:
  high_quality:
    cleanroom_class: 1
    quality_base_rate: 0.9999
```

## Example: Complete Factory Without Python Code (NEW)

With the subsystem_implementations feature, you can now define a complete factory including both WHAT exists (resources, recipes) and HOW it behaves (subsystem implementations) entirely through specs:

```yaml
metadata:
  name: "AI-Optimized Smart Factory"
  version: "2.0.0"
  description: "Fully autonomous factory using AI and ML optimization"
  parent: "minimal.json"  # Inherit basic resources and recipes

# Define which subsystem implementations to use
subsystem_implementations:
  transport: "genetic_routing"         # Use genetic algorithms for routing
  maintenance: "predictive_maintenance"  # ML-based failure prediction
  quality: "spc_quality"              # Statistical process control
  energy: "smart_grid"                # Smart grid integration
  energy_optimizer: "renewable_optimizer"  # Renewable energy optimization
  monitoring: "digital_twin"          # Digital twin simulation

# Configure each subsystem's behavior
subsystem_data:
  transport:
    population_size: 200
    mutation_rate: 0.1
    crossover_rate: 0.8
    elite_size: 20
    max_generations: 100

  maintenance:
    failure_threshold: 0.7
    predictive_horizon_hours: 336  # 2 weeks lookahead
    min_reliability: 0.99
    redundancy_factor: 2.0

  quality:
    control_limits_sigma: 6        # Six Sigma quality
    sample_size: 30
    target_cpk: 2.0
    auto_correction: true

  energy:
    grid_connection: true
    grid_buy_price: 0.15
    grid_sell_price: 0.10
    demand_response: true
    battery_strategy: "economic"

  monitoring:
    simulation_timestep: 0.05
    prediction_horizon: 200
    optimization_objective: "efficiency"

# Define configuration profiles
profiles:
  learning_mode:
    description: "Aggressive learning for rapid optimization"
    subsystem_data:
      transport:
        mutation_rate: 0.25
        max_generations: 200

  production_mode:
    description: "Stable production with proven parameters"
    subsystem_data:
      transport:
        mutation_rate: 0.05
        elite_size: 50

constraints:
  enable_weather: true
  enable_thermal_management: true
  parallel_processing_limit: 20
```

To run this fully configured factory:

```bash
# No Python code needed - everything defined in the spec!
python3 self_replicating_factory_sim.py --spec my_smart_factory.yaml --modular --profile learning_mode
```

This achieves "full universality" - the spec defines both the factory's physical configuration (resources, recipes, modules) and its behavioral implementation (which algorithms and strategies to use).

## Troubleshooting

### Common Issues

1. **"Recipe output 'X' not defined in resources"**
   - Add the missing resource to the resources section

2. **"Dependency cycle detected"**
   - Check for circular dependencies in recipes
   - Ensure raw materials have no inputs

3. **"Required module 'X' not defined"**
   - Add the module to the modules section

4. **Spec not loading**
   - Check file path is correct
   - Verify YAML/JSON syntax
   - Look for validation errors in output

### Debugging

Enable verbose output by modifying spec_loader.py or adding debug prints to see:
- What resources are loaded
- Recipe dependency graph
- Module configurations
- Validation results

## API Reference

### SpecLoader Class

```python
from spec_loader import SpecLoader

loader = SpecLoader()
spec = loader.load_spec("specs/minimal.spec")
resource_enum = loader.create_resource_enum(spec)
recipes = loader.create_recipes(spec, resource_enum)
module_specs = loader.create_module_specs(spec)
config = loader.create_config(spec, profile="high_throughput")
```

### SpecRegistry Class

```python
from spec_loader import SpecRegistry

registry = SpecRegistry()
available = registry.list_specs()
spec = registry.load("minimal")
description = registry.get_description("minimal")
```

### Factory Builder (NEW)

Create fully configured modular factories from specs:

```python
from factory_builder import create_factory_from_spec
from modular_framework import UpdateStrategy

# Create factory with spec-defined subsystems
factory = create_factory_from_spec(
    "specs/genetic_optimized.json",
    profile="aggressive",
    update_strategy=UpdateStrategy.PARALLEL
)

# Run simulation - no Python code needed for configuration!
result = factory.run_simulation(max_hours=1000)
```

List available subsystems:

```python
from factory_builder import list_available_subsystems, validate_spec_subsystems

# See what subsystems can be used in specs
subsystems = list_available_subsystems()

# Validate a spec's subsystem implementations
is_valid = validate_spec_subsystems("specs/genetic_optimized.json")
```

## Contributing

To contribute new spec templates:

1. Create spec in `specs/` directory
2. Test thoroughly with simulation
3. Document unique features
4. Submit with example results

## Future Enhancements

Planned improvements:
- GUI spec editor
- Automatic dependency resolution
- Recipe optimization algorithms
- Spec merging tools
- Performance profiling per spec
- Cloud-based spec sharing
- Visual subsystem designer
- Hot-reload for spec changes during simulation
- Distributed factory simulation across multiple specs