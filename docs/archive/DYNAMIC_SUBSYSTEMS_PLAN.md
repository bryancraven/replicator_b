# Plan: Making Subsystems Fully Dynamic

## Problem Analysis

The current factory simulation has several subsystems with hardcoded `ResourceType` enum references that prevent full dynamic configuration through the spec system. When loading a spec with different resources, these hardcoded references cause `AttributeError` exceptions.

### Affected Subsystems

1. **WasteStream** (`self_replicating_factory_sim.py:1238-1250`)
   - Hardcoded recyclable materials dictionary
   - References: STEEL, ALUMINUM_SHEET, COPPER_WIRE, PLASTIC, GLASS, SILICON_WAFER

2. **SoftwareProductionSystem** (`self_replicating_factory_sim.py:1376-1385`)
   - Hardcoded bug rates dictionary
   - References: PLC_PROGRAM, ROBOT_FIRMWARE, AI_MODEL, SCADA_SYSTEM

3. **StorageSystem** (`self_replicating_factory_sim.py:1533-1543`)
   - Hardcoded MATERIAL_PROPERTIES dictionary
   - References: SILICON_ORE, IRON_ORE, SILICON_WAFER, INTEGRATED_CIRCUIT, CHEMICAL_PUMP, LITHIUM_COMPOUND, SULFURIC_ACID, ORGANIC_SOLVENT

4. **Factory.calculate_requirements** (`self_replicating_factory_sim.py:2324-2345`)
   - Hardcoded list of factory module types
   - References: MINING_MODULE, REFINING_MODULE, CHEMICAL_MODULE, etc.

## Solution Architecture

### 1. Configuration-Driven Subsystems

Instead of hardcoding resource properties, move them to the spec configuration:

```yaml
# In spec file
subsystem_data:
  waste_stream:
    recyclable_materials:
      STEEL: 0.95
      ALUMINUM_SHEET: 0.90
      COPPER_WIRE: 0.85
      PLASTIC: 0.60
      GLASS: 0.80
      SILICON_WAFER: 0.70

  software_production:
    bug_rates:
      PLC_PROGRAM: 0.05
      ROBOT_FIRMWARE: 0.08
      AI_MODEL: 0.15
      SCADA_SYSTEM: 0.10

  storage:
    material_properties:
      SILICON_ORE:
        density: 2.3
        storage_temp: 25
        contamination_sensitivity: 0.1
```

### 2. Dynamic Initialization Pattern

Create a new initialization system that:
1. Accepts configuration data at runtime
2. Maps string resource names to enum values dynamically
3. Falls back to defaults when data is missing

```python
class DynamicSubsystem:
    def __init__(self, config: Dict, resource_enum: Enum):
        self.resource_enum = resource_enum
        self.config = config
        self._initialize_from_config()

    def _initialize_from_config(self):
        # Convert string keys to enum values
        for key, value in self.config.items():
            if hasattr(self.resource_enum, key):
                enum_val = getattr(self.resource_enum, key)
                # Use enum_val as key
```

### 3. Subsystem Factory Pattern

Create a factory that builds subsystems with the correct configuration:

```python
class SubsystemFactory:
    def __init__(self, spec: FactorySpec, resource_enum: Enum):
        self.spec = spec
        self.resource_enum = resource_enum

    def create_waste_stream(self):
        config = self.spec.subsystem_data.get('waste_stream', {})
        return DynamicWasteStream(config, self.resource_enum)

    def create_software_system(self):
        config = self.spec.subsystem_data.get('software_production', {})
        return DynamicSoftwareSystem(config, self.resource_enum)
```

## Implementation Steps

### Phase 1: Create Dynamic Subsystem Classes
**Files:** `dynamic_subsystems.py` (new)

1. Create `DynamicWasteStream` class
   - Accept recyclable_materials as config
   - Convert string keys to ResourceType dynamically
   - Maintain same interface as WasteStream

2. Create `DynamicSoftwareProductionSystem` class
   - Accept bug_rates as config
   - Handle missing software types gracefully

3. Create `DynamicStorageSystem` class
   - Accept material_properties as config
   - Use spec-defined properties or defaults

### Phase 2: Update Spec Format
**Files:** `spec_loader.py`, `SPEC_FORMAT.md`

1. Add `subsystem_data` section to spec schema
2. Update SpecLoader to parse subsystem configurations
3. Add validation for subsystem data
4. Update documentation

### Phase 3: Integrate Dynamic Subsystems
**Files:** `self_replicating_factory_sim.py`

1. Modify Factory.__init__() to:
   - Check if running with spec
   - Use SubsystemFactory when spec is loaded
   - Fall back to original subsystems for backward compatibility

2. Update main() to:
   - Pass spec data to Factory
   - Initialize SubsystemFactory with resource enum

### Phase 4: Update Module Requirements
**Files:** `self_replicating_factory_sim.py`

1. Make factory module list configurable:
   - Move to spec configuration
   - Allow specs to define which modules to build
   - Support partial factory configurations

### Phase 5: Testing & Migration
**Files:** `test_dynamic_subsystems.py` (new)

1. Create test suite for dynamic subsystems
2. Test with various spec configurations
3. Verify backward compatibility
4. Performance testing

## Benefits

1. **Complete Flexibility**: Any resource set can be defined without code changes
2. **Maintainability**: Resource properties live in configuration, not code
3. **Extensibility**: New subsystems can be added without modifying core code
4. **Backward Compatibility**: Existing simulations continue to work
5. **Testing**: Easier to test with different configurations

## Example Usage

```python
# With spec loading
spec = loader.load_spec("custom_factory.spec")
resource_enum = loader.create_resource_enum(spec)
factory = Factory(config, spec=spec, resource_enum=resource_enum)

# Without spec (backward compatible)
factory = Factory(CONFIG)  # Uses default hardcoded values
```

## Risk Mitigation

1. **Performance**: Cache enum lookups to avoid repeated string comparisons
2. **Type Safety**: Add validation to ensure all referenced resources exist
3. **Debugging**: Add logging for dynamic resource resolution
4. **Migration**: Provide migration script for existing specs

## Timeline

- **Week 1**: Implement Phase 1-2 (Dynamic subsystem classes & spec format)
- **Week 2**: Implement Phase 3-4 (Integration & module requirements)
- **Week 3**: Testing, debugging, documentation
- **Week 4**: Migration tools and performance optimization

## Alternative Approaches Considered

1. **String-based resources throughout**: Rejected due to performance concerns
2. **Code generation from specs**: Rejected as too complex
3. **Plugin system**: Rejected as overkill for current needs
4. **Monkey-patching ResourceType**: Rejected as too fragile

## Success Metrics

- All existing tests pass
- New specs can define arbitrary resources without errors
- No performance regression (< 5% slower)
- Zero hardcoded ResourceType references in subsystems
- Documentation complete with examples