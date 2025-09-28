#!/usr/bin/env python3
"""
Spec Loader System for Modular Factory Simulation

This module provides functionality to load, validate, and manage factory
specifications from external files, enabling dynamic factory configurations.
"""

import json
import os

# Try to import yaml, but make it optional
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available. Only JSON specs will be supported.")
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from collections import defaultdict
import copy


# ===============================================================================
# SPEC DATA STRUCTURES
# ===============================================================================

@dataclass
class ResourceSpec:
    """Specification for a resource/component"""
    name: str
    density: float = 1.0  # tons/m³
    storage_temp: float = 25.0  # °C
    contamination_sensitivity: float = 0.5  # 0-1 scale
    hazardous: bool = False
    recyclable: bool = True
    volume_per_unit: float = 0.001  # m³
    description: str = ""


@dataclass
class RecipeSpec:
    """Specification for a production recipe"""
    output: str
    output_quantity: int
    inputs: Dict[str, float]
    energy_kwh: float
    time_hours: float
    required_module: Optional[str] = None
    parallel_capable: bool = True
    tolerance_um: Optional[float] = None
    cleanroom_class: Optional[int] = None
    software_required: Optional[str] = None
    waste_products: Optional[Dict[str, float]] = None


@dataclass
class ModuleSpecData:
    """Specification for a module type"""
    module_type: str
    max_throughput: float
    power_consumption_idle: float
    power_consumption_active: float
    mtbf_hours: float = 5000
    maintenance_interval: float = 500
    degradation_rate: float = 0.02
    physical_footprint: float = 100
    max_batch_size: int = 100
    min_batch_size: int = 1
    setup_time: float = 1.0
    quality_base_rate: float = 0.95
    tolerance_capability: Optional[float] = None
    cleanroom_capable: bool = False


@dataclass
class FactorySpec:
    """Complete factory specification"""
    metadata: Dict[str, Any]
    resources: Dict[str, ResourceSpec]
    recipes: List[RecipeSpec]
    modules: Dict[str, ModuleSpecData]
    initial_state: Dict[str, Any]
    constraints: Dict[str, Any]
    subsystems: Dict[str, Any]
    profiles: Dict[str, Any] = field(default_factory=dict)
    subsystem_data: Dict[str, Any] = field(default_factory=dict)
    target_modules: List[str] = field(default_factory=list)
    subsystem_implementations: Dict[str, str] = field(default_factory=dict)


# ===============================================================================
# SPEC LOADER
# ===============================================================================

class SpecLoader:
    """Loads and manages factory specifications"""

    def __init__(self, spec_dir: str = "specs"):
        self.spec_dir = spec_dir
        self.loaded_specs: Dict[str, FactorySpec] = {}
        self.current_spec: Optional[FactorySpec] = None

    def load_spec(self, spec_path: str) -> FactorySpec:
        """Load a spec file and resolve any inheritance"""
        # Resolve full path
        if not os.path.isabs(spec_path):
            spec_path = os.path.join(self.spec_dir, spec_path)

        # Check if already loaded
        if spec_path in self.loaded_specs:
            return self.loaded_specs[spec_path]

        # Load the spec file
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.json'):
                spec_data = json.load(f)
            elif spec_path.endswith(('.yaml', '.yml', '.spec')):
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML is required to load YAML/spec files. Install with: pip install pyyaml")
                spec_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported spec file format: {spec_path}")

        # Handle recipes_file reference
        if 'recipes_file' in spec_data:
            recipes_path = spec_data['recipes_file']
            if not os.path.isabs(recipes_path):
                recipes_path = os.path.join(os.path.dirname(spec_path), recipes_path)
            with open(recipes_path, 'r') as f:
                if recipes_path.endswith('.json'):
                    recipes_data = json.load(f)
                else:
                    if not YAML_AVAILABLE:
                        raise ImportError("PyYAML is required to load YAML recipe files")
                    recipes_data = yaml.safe_load(f)
                if 'recipes' in recipes_data:
                    spec_data['recipes'] = recipes_data['recipes']

        # Handle inheritance
        if 'metadata' in spec_data and 'parent' in spec_data['metadata']:
            parent_path = spec_data['metadata']['parent']
            if not os.path.isabs(parent_path):
                parent_path = os.path.join(os.path.dirname(spec_path), parent_path)
            parent_spec = self.load_spec(parent_path)
            spec_data = self._merge_specs(parent_spec.__dict__, spec_data)

        # Parse into FactorySpec
        factory_spec = self._parse_spec_data(spec_data)

        # Validate the spec
        self._validate_spec(factory_spec)

        # Cache and return
        self.loaded_specs[spec_path] = factory_spec
        self.current_spec = factory_spec
        return factory_spec

    def _merge_specs(self, parent: Dict, child: Dict) -> Dict:
        """Merge child spec into parent spec with deep merging"""
        result = copy.deepcopy(parent)

        for key, value in child.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_specs(result[key], value)
            else:
                result[key] = value

        return result

    def _parse_spec_data(self, spec_data: Dict) -> FactorySpec:
        """Parse raw spec data into FactorySpec objects"""
        # Parse resources
        resources = {}
        for name, props in spec_data.get('resources', {}).items():
            if isinstance(props, dict):
                resources[name] = ResourceSpec(name=name, **props)
            else:
                resources[name] = ResourceSpec(name=name)

        # Parse recipes
        recipes = []
        for recipe_data in spec_data.get('recipes', []):
            recipes.append(RecipeSpec(**recipe_data))

        # Parse modules
        modules = {}
        for name, props in spec_data.get('modules', {}).items():
            if isinstance(props, dict):
                modules[name] = ModuleSpecData(module_type=name, **props)
            else:
                modules[name] = ModuleSpecData(module_type=name)

        return FactorySpec(
            metadata=spec_data.get('metadata', {}),
            resources=resources,
            recipes=recipes,
            modules=modules,
            initial_state=spec_data.get('initial_state', {}),
            constraints=spec_data.get('constraints', {}),
            subsystems=spec_data.get('subsystems', {}),
            profiles=spec_data.get('profiles', {}),
            subsystem_data=spec_data.get('subsystem_data', {}),
            target_modules=spec_data.get('target_modules', []),
            subsystem_implementations=spec_data.get('subsystem_implementations', {})
        )

    def _validate_spec(self, spec: FactorySpec):
        """Validate the spec for consistency and completeness"""
        validator = SpecValidator()
        validator.validate(spec)

    def create_resource_enum(self, spec: Optional[FactorySpec] = None):
        """Create ResourceType enum from spec"""
        spec = spec or self.current_spec
        if not spec:
            raise ValueError("No spec loaded")

        # Create enum with resource names
        enum_dict = {name: name.lower() for name in spec.resources.keys()}
        return Enum('ResourceType', enum_dict)

    def create_recipes(self, spec: Optional[FactorySpec] = None, resource_enum: Optional[Enum] = None):
        """Create Recipe objects from spec"""
        spec = spec or self.current_spec
        if not spec:
            raise ValueError("No spec loaded")

        if not resource_enum:
            resource_enum = self.create_resource_enum(spec)

        # Import Recipe class
        from self_replicating_factory_sim import Recipe

        recipes = []
        for recipe_spec in spec.recipes:
            # Convert string references to enum values
            output = getattr(resource_enum, recipe_spec.output)
            inputs = {}
            for input_name, quantity in recipe_spec.inputs.items():
                inputs[getattr(resource_enum, input_name)] = quantity

            # Handle optional software requirement
            software_req = None
            if recipe_spec.software_required:
                software_req = getattr(resource_enum, recipe_spec.software_required)

            # Handle waste products
            waste = {}
            if recipe_spec.waste_products:
                for waste_name, quantity in recipe_spec.waste_products.items():
                    waste[getattr(resource_enum, waste_name)] = quantity

            recipes.append(Recipe(
                output=output,
                output_quantity=recipe_spec.output_quantity,
                inputs=inputs,
                energy_kwh=recipe_spec.energy_kwh,
                time_hours=recipe_spec.time_hours,
                required_module=recipe_spec.required_module,
                parallel_capable=recipe_spec.parallel_capable,
                tolerance_um=recipe_spec.tolerance_um,
                cleanroom_class=recipe_spec.cleanroom_class,
                software_required=software_req,
                waste_products=waste if waste else None
            ))

        return recipes

    def create_module_specs(self, spec: Optional[FactorySpec] = None):
        """Create ModuleSpec objects from spec"""
        spec = spec or self.current_spec
        if not spec:
            raise ValueError("No spec loaded")

        # Import ModuleSpec class
        from self_replicating_factory_sim import ModuleSpec

        module_specs = {}
        for name, spec_data in spec.modules.items():
            module_specs[name] = ModuleSpec(
                module_type=spec_data.module_type,
                max_throughput=spec_data.max_throughput,
                power_consumption_idle=spec_data.power_consumption_idle,
                power_consumption_active=spec_data.power_consumption_active,
                mtbf_hours=spec_data.mtbf_hours,
                maintenance_interval=spec_data.maintenance_interval,
                degradation_rate=spec_data.degradation_rate,
                physical_footprint=spec_data.physical_footprint,
                max_batch_size=spec_data.max_batch_size,
                min_batch_size=spec_data.min_batch_size,
                setup_time=spec_data.setup_time,
                quality_base_rate=spec_data.quality_base_rate,
                tolerance_capability=spec_data.tolerance_capability
            )

        return module_specs

    def create_config(self, spec: Optional[FactorySpec] = None, profile: Optional[str] = None):
        """Create CONFIG dictionary from spec"""
        spec = spec or self.current_spec
        if not spec:
            raise ValueError("No spec loaded")

        # Start with constraints as base config
        config = copy.deepcopy(spec.constraints)

        # Add subsystem configs
        for key, value in spec.subsystems.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    config[f"{key}_{sub_key}"] = sub_value
            else:
                config[key] = value

        # Apply profile if specified
        if profile and profile in spec.profiles:
            profile_data = spec.profiles[profile]
            for key, value in profile_data.items():
                if key != "description":
                    config[key] = value

        return config


# ===============================================================================
# SPEC VALIDATOR
# ===============================================================================

class SpecValidator:
    """Validates factory specifications"""

    def validate(self, spec: FactorySpec):
        """Validate a factory spec for consistency"""
        errors = []
        warnings = []

        # Check for resource references in recipes
        resource_names = set(spec.resources.keys())
        for recipe in spec.recipes:
            # Check output
            if recipe.output not in resource_names:
                errors.append(f"Recipe output '{recipe.output}' not defined in resources")

            # Check inputs
            for input_name in recipe.inputs.keys():
                if input_name not in resource_names:
                    errors.append(f"Recipe input '{input_name}' not defined in resources")

            # Check software requirement
            if recipe.software_required and recipe.software_required not in resource_names:
                errors.append(f"Software requirement '{recipe.software_required}' not defined")

            # Check waste products
            if recipe.waste_products:
                for waste_name in recipe.waste_products.keys():
                    if waste_name not in resource_names:
                        warnings.append(f"Waste product '{waste_name}' not defined in resources")

            # Check module requirement
            if recipe.required_module and recipe.required_module not in spec.modules:
                errors.append(f"Required module '{recipe.required_module}' not defined")

        # Check for dependency cycles
        cycles = self._check_dependency_cycles(spec)
        if cycles:
            for cycle in cycles:
                errors.append(f"Dependency cycle detected: {' -> '.join(cycle)}")

        # Check module specifications
        for name, module in spec.modules.items():
            if module.max_throughput <= 0:
                errors.append(f"Module '{name}' has invalid throughput: {module.max_throughput}")
            if module.power_consumption_active < module.power_consumption_idle:
                warnings.append(f"Module '{name}' active power less than idle power")

        # Raise exception if errors found
        if errors:
            error_msg = "Spec validation failed:\n" + "\n".join(errors)
            if warnings:
                error_msg += "\nWarnings:\n" + "\n".join(warnings)
            raise ValueError(error_msg)
        elif warnings:
            print("Spec validation warnings:")
            for warning in warnings:
                print(f"  - {warning}")

    def _check_dependency_cycles(self, spec: FactorySpec) -> List[List[str]]:
        """Check for cycles in the recipe dependency graph"""
        # Build dependency graph
        graph = defaultdict(set)
        for recipe in spec.recipes:
            for input_name in recipe.inputs.keys():
                graph[recipe.output].add(input_name)

        # Use DFS to detect cycles
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    # Cycle found
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)
            return False

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node, [])

        return cycles


# ===============================================================================
# SPEC REGISTRY
# ===============================================================================

class SpecRegistry:
    """Registry for managing multiple specs"""

    def __init__(self, spec_dir: str = "specs"):
        self.spec_dir = spec_dir
        self.loader = SpecLoader(spec_dir)
        self.available_specs = {}
        self._scan_specs()

    def _scan_specs(self):
        """Scan spec directory for available specs"""
        for root, dirs, files in os.walk(self.spec_dir):
            for file in files:
                if file.endswith(('.spec', '.yaml', '.yml', '.json')):
                    rel_path = os.path.relpath(os.path.join(root, file), self.spec_dir)
                    spec_name = os.path.splitext(rel_path)[0]
                    self.available_specs[spec_name] = rel_path

    def list_specs(self) -> List[str]:
        """List available spec names"""
        return list(self.available_specs.keys())

    def load(self, spec_name: str) -> FactorySpec:
        """Load a spec by name"""
        if spec_name not in self.available_specs:
            raise ValueError(f"Spec '{spec_name}' not found. Available: {self.list_specs()}")
        return self.loader.load_spec(self.available_specs[spec_name])

    def get_description(self, spec_name: str) -> str:
        """Get description of a spec without fully loading it"""
        spec = self.load(spec_name)
        return spec.metadata.get('description', 'No description available')


# ===============================================================================
# UTILITY FUNCTIONS
# ===============================================================================

def load_factory_spec(spec_path: str = "default.spec") -> Tuple[Any, List, Dict, Dict]:
    """
    Load a factory spec and return configured objects

    Returns:
        (ResourceType enum, recipes list, module_specs dict, config dict)
    """
    loader = SpecLoader()
    spec = loader.load_spec(spec_path)

    resource_enum = loader.create_resource_enum(spec)
    recipes = loader.create_recipes(spec, resource_enum)
    module_specs = loader.create_module_specs(spec)
    config = loader.create_config(spec)

    return resource_enum, recipes, module_specs, config


# ===============================================================================
# EXAMPLE USAGE
# ===============================================================================

if __name__ == "__main__":
    # Example: Load and validate a spec
    registry = SpecRegistry()
    print("Available specs:", registry.list_specs())

    # Load default spec if it exists
    if os.path.exists("specs/default.spec"):
        try:
            loader = SpecLoader()
            spec = loader.load_spec("specs/default.spec")
            print(f"Loaded spec: {spec.metadata.get('name', 'Unknown')}")
            print(f"Resources: {len(spec.resources)}")
            print(f"Recipes: {len(spec.recipes)}")
            print(f"Modules: {len(spec.modules)}")
        except Exception as e:
            print(f"Error loading spec: {e}")
    else:
        print("No default.spec found. Create one with spec definitions.")