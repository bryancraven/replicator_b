# Dynamic Subsystems Migration Guide

## Overview
This guide helps you migrate from hardcoded ResourceType references to the new dynamic subsystem architecture.

## Migration Benefits
- **Complete Flexibility**: Define any resource set without code changes
- **Spec-Based Configuration**: All factory parameters in external files
- **Backward Compatibility**: Existing code continues to work
- **Dynamic Module Lists**: Customize which modules to build
- **Subsystem Configuration**: Configure waste, storage, and software parameters

## Quick Migration

### Step 1: Create Your Spec File
Create a JSON spec file defining your factory configuration:

```json
{
  "metadata": {
    "name": "My Custom Factory",
    "version": "1.0.0"
  },
  "resources": {
    "IRON_ORE": {
      "density": 4.0,
      "storage_temp": 25
    },
    "STEEL": {
      "density": 7.8,
      "storage_temp": 25
    }
  },
  "recipes": [
    {
      "output": "STEEL",
      "output_quantity": 100,
      "inputs": {"IRON_ORE": 150},
      "energy_kwh": 50,
      "time_hours": 2.0
    }
  ],
  "target_modules": [
    "MINING_MODULE",
    "REFINING_MODULE"
  ],
  "subsystem_data": {
    "waste_stream": {
      "recyclable_materials": {
        "STEEL": 0.95
      }
    }
  }
}
```

### Step 2: Run with Spec
```bash
python3 self_replicating_factory_sim.py --spec my_factory.json
```

## Detailed Migration Steps

### 1. Migrating Resources
**Before** (hardcoded):
```python
class ResourceType(Enum):
    IRON_ORE = "iron_ore"
    STEEL = "steel"
```

**After** (in spec):
```json
"resources": {
  "IRON_ORE": {"density": 4.0},
  "STEEL": {"density": 7.8}
}
```

### 2. Migrating Recipes
**Before** (in code):
```python
Recipe(
    output=ResourceType.STEEL,
    inputs={ResourceType.IRON_ORE: 150},
    energy_kwh=50,
    time_hours=2.0
)
```

**After** (in spec):
```json
"recipes": [
  {
    "output": "STEEL",
    "inputs": {"IRON_ORE": 150},
    "energy_kwh": 50,
    "time_hours": 2.0
  }
]
```

### 3. Migrating Subsystem Configuration
**Before** (hardcoded in WasteStream):
```python
self.recyclable_materials = {
    ResourceType.STEEL: 0.95,
    ResourceType.ALUMINUM_SHEET: 0.90
}
```

**After** (in spec):
```json
"subsystem_data": {
  "waste_stream": {
    "recyclable_materials": {
      "STEEL": 0.95,
      "ALUMINUM_SHEET": 0.90
    }
  }
}
```

### 4. Migrating Module Lists
**Before** (hardcoded list):
```python
module_types = [
    ResourceType.MINING_MODULE,
    ResourceType.REFINING_MODULE,
    # ... all 16 modules
]
```

**After** (in spec):
```json
"target_modules": [
  "MINING_MODULE",
  "REFINING_MODULE"
]
```

## Subsystem Configuration Options

### Waste Stream
```json
"subsystem_data": {
  "waste_stream": {
    "recyclable_materials": {
      "STEEL": 0.95,
      "PLASTIC": 0.60
    }
  }
}
```

### Software Production
```json
"subsystem_data": {
  "software_production": {
    "bug_rates": {
      "PLC_PROGRAM": 0.05,
      "ROBOT_FIRMWARE": 0.08
    },
    "development_hours": {
      "PLC_PROGRAM": 100
    }
  }
}
```

### Storage System
```json
"subsystem_data": {
  "storage": {
    "material_properties": {
      "IRON_ORE": [4.0, 25, 0.1],
      "CHEMICAL_REAGENT": [1.2, 15, 0.9]
    }
  }
}
```

## Testing Your Migration

### 1. Validate Spec
```python
from spec_loader import SpecLoader

loader = SpecLoader()
spec = loader.load_spec("my_factory.json")
print(f"Loaded {len(spec.resources)} resources")
print(f"Loaded {len(spec.recipes)} recipes")
```

### 2. Test Dynamic Subsystems
```python
from dynamic_subsystems import SubsystemFactory

factory = SubsystemFactory(spec=spec_dict, resource_enum=ResourceType)
waste = factory.create_waste_stream()
print(f"Configured {len(waste.recyclable_materials)} recyclable materials")
```

### 3. Run Simulation
```bash
# Test with short duration
python3 self_replicating_factory_sim.py --spec my_factory.json --max-hours 100
```

## Backward Compatibility

The system maintains full backward compatibility:

1. **Without Spec**: Factory uses default hardcoded configuration
   ```bash
   python3 self_replicating_factory_sim.py
   ```

2. **With Spec**: Factory uses dynamic configuration
   ```bash
   python3 self_replicating_factory_sim.py --spec minimal.json
   ```

3. **Mixed Mode**: You can use spec for some parts and defaults for others

## Common Issues and Solutions

### Issue 1: Resource Not Found
**Error**: `AttributeError: ResourceType has no attribute 'MY_RESOURCE'`
**Solution**: Ensure the resource is defined in your spec's `resources` section

### Issue 2: Recipe Missing Inputs
**Error**: `Recipe input 'COMPONENT_X' not defined in resources`
**Solution**: Add all recipe inputs to the `resources` section

### Issue 3: Module Not Building
**Problem**: A module isn't being created
**Solution**: Add it to the `target_modules` list in your spec

### Issue 4: Subsystem Not Configured
**Problem**: Dynamic subsystem using defaults instead of spec values
**Solution**: Ensure `subsystem_data` section includes configuration for that subsystem

## Advanced Migration

### Custom Subsystems
You can create entirely new subsystems:

```python
from dynamic_subsystems import DynamicSubsystemBase

class MyCustomSubsystem(DynamicSubsystemBase):
    def __init__(self, config=None, resource_enum=None):
        super().__init__(config, resource_enum)
        # Your initialization
```

### Profile-Based Configuration
Use profiles for different scenarios:

```json
"profiles": {
  "high_throughput": {
    "parallel_processing_limit": 10,
    "agv_fleet_size": 20
  },
  "energy_efficient": {
    "solar_panel_efficiency": 0.30,
    "battery_efficiency": 0.98
  }
}
```

Run with profile:
```bash
python3 self_replicating_factory_sim.py --spec my_factory.json --profile high_throughput
```

## Migration Checklist

- [ ] Create spec file with resources
- [ ] Define recipes in spec
- [ ] Configure target_modules list
- [ ] Add subsystem_data configuration
- [ ] Test with short simulation
- [ ] Verify backward compatibility
- [ ] Run comprehensive tests
- [ ] Document custom configurations

## Getting Help

- See `SPEC_FORMAT.md` for complete spec documentation
- See `DYNAMIC_SUBSYSTEMS_PLAN.md` for architecture details
- Run `python3 test_dynamic_complete.py` to verify your setup
- Check `specs/minimal.json` for a working example