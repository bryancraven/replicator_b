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
```

### Available Specs

- **`specs/default.spec`**: Ultra-realistic factory with 250+ components and 16 modules
- **`specs/minimal.spec`**: Simplified factory with ~50 components for faster simulation

## Spec File Structure

A spec file contains the following sections:

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