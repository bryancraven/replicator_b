#!/usr/bin/env python3
"""
Unit tests for spec_loader module
"""

import pytest
import json
from pathlib import Path

from spec_loader import (
    SpecLoader,
    SpecValidator,
    SpecRegistry,
    ResourceSpec,
    RecipeSpec,
    ModuleSpecData,
    FactorySpec,
)
from exceptions import (
    SpecNotFoundError,
    SpecParseError,
    SpecValidationError,
    CircularDependencyError,
)


class TestResourceSpec:
    """Test ResourceSpec dataclass"""

    def test_resource_spec_creation_minimal(self):
        """Test creating resource spec with minimal parameters"""
        spec = ResourceSpec(name="STEEL")
        assert spec.name == "STEEL"
        assert spec.density == 1.0  # Default
        assert spec.recyclable is True  # Default

    def test_resource_spec_creation_full(self):
        """Test creating resource spec with all parameters"""
        spec = ResourceSpec(
            name="SILICON_WAFER",
            density=2.3,
            storage_temp=22.0,
            contamination_sensitivity=1.0,
            hazardous=False,
            recyclable=True,
            volume_per_unit=0.001,
            description="High-purity silicon wafer"
        )

        assert spec.name == "SILICON_WAFER"
        assert spec.density == 2.3
        assert spec.storage_temp == 22.0
        assert spec.contamination_sensitivity == 1.0
        assert spec.hazardous is False
        assert spec.description == "High-purity silicon wafer"


class TestRecipeSpec:
    """Test RecipeSpec dataclass"""

    def test_recipe_spec_creation(self):
        """Test creating recipe spec"""
        spec = RecipeSpec(
            output="STEEL",
            output_quantity=10,
            inputs={"IRON_ORE": 15},
            energy_kwh=100,
            time_hours=2.0,
            required_module="smelter"
        )

        assert spec.output == "STEEL"
        assert spec.output_quantity == 10
        assert spec.inputs["IRON_ORE"] == 15
        assert spec.energy_kwh == 100
        assert spec.time_hours == 2.0
        assert spec.required_module == "smelter"

    def test_recipe_spec_with_optional_fields(self):
        """Test recipe spec with optional fields"""
        spec = RecipeSpec(
            output="SILICON_WAFER",
            output_quantity=1,
            inputs={"SILICON": 1},
            energy_kwh=50,
            time_hours=5.0,
            required_module="cleanroom",
            tolerance_um=0.1,
            cleanroom_class=100,
            software_required="PLC_PROGRAM",
            waste_products={"SILICON_DUST": 0.1}
        )

        assert spec.tolerance_um == 0.1
        assert spec.cleanroom_class == 100
        assert spec.software_required == "PLC_PROGRAM"
        assert spec.waste_products["SILICON_DUST"] == 0.1


class TestModuleSpecData:
    """Test ModuleSpecData dataclass"""

    def test_module_spec_creation(self):
        """Test creating module spec"""
        spec = ModuleSpecData(
            module_type="cnc",
            max_throughput=100.0,
            power_consumption_idle=10.0,
            power_consumption_active=100.0
        )

        assert spec.module_type == "cnc"
        assert spec.max_throughput == 100.0
        assert spec.power_consumption_idle == 10.0
        assert spec.power_consumption_active == 100.0
        # Check defaults
        assert spec.mtbf_hours == 5000
        assert spec.degradation_rate == 0.02


class TestSpecLoader:
    """Test SpecLoader class"""

    def test_spec_loader_creation(self):
        """Test creating a spec loader"""
        loader = SpecLoader()
        assert loader.spec_dir == "specs"
        assert len(loader.loaded_specs) == 0

    def test_spec_loader_custom_directory(self):
        """Test creating loader with custom directory"""
        loader = SpecLoader(spec_dir="custom/path")
        assert loader.spec_dir == "custom/path"

    def test_load_minimal_spec(self, minimal_spec_file):
        """Test loading a minimal spec file"""
        loader = SpecLoader()
        spec = loader.load_spec(minimal_spec_file)

        assert isinstance(spec, FactorySpec)
        assert spec.metadata["name"] == "Test Factory"
        assert "IRON_ORE" in spec.resources
        assert "STEEL" in spec.resources
        assert len(spec.recipes) == 1

    def test_load_nonexistent_spec(self):
        """Test loading non-existent spec file raises error"""
        loader = SpecLoader()

        with pytest.raises(SpecNotFoundError) as exc_info:
            loader.load_spec("/path/to/nonexistent.spec")

        assert "/path/to/nonexistent.spec" in str(exc_info.value)

    def test_load_spec_cached(self, minimal_spec_file):
        """Test that specs are cached after first load"""
        loader = SpecLoader()

        spec1 = loader.load_spec(minimal_spec_file)
        spec2 = loader.load_spec(minimal_spec_file)

        # Should return same instance
        assert spec1 is spec2

    def test_parse_invalid_json(self, temp_spec_dir):
        """Test parsing invalid JSON raises error"""
        invalid_spec = temp_spec_dir / "invalid.json"
        with open(invalid_spec, 'w') as f:
            f.write("{ invalid json }")

        loader = SpecLoader()
        with pytest.raises(SpecParseError) as exc_info:
            loader.load_spec(str(invalid_spec))

        assert "invalid.json" in str(exc_info.value)

    def test_create_resource_enum(self, minimal_factory_spec):
        """Test creating ResourceType enum from spec"""
        loader = SpecLoader()
        loader.current_spec = minimal_factory_spec

        resource_enum = loader.create_resource_enum()

        assert hasattr(resource_enum, 'IRON_ORE')
        assert hasattr(resource_enum, 'STEEL')
        assert hasattr(resource_enum, 'STEEL_BEAM')

    def test_create_config_from_spec(self, minimal_factory_spec):
        """Test creating CONFIG from spec"""
        loader = SpecLoader()
        loader.current_spec = minimal_factory_spec

        config = loader.create_config()

        assert config["enable_capacity_limits"] is True
        assert config["parallel_processing_limit"] == 5


class TestSpecValidator:
    """Test SpecValidator class"""

    def test_validate_valid_spec(self, minimal_factory_spec):
        """Test validating a valid spec"""
        validator = SpecValidator()

        # Should not raise
        validator.validate(minimal_factory_spec)

    def test_validate_missing_resource(self):
        """Test validation fails for missing resource"""
        spec = FactorySpec(
            metadata={},
            resources={"IRON_ORE": ResourceSpec(name="IRON_ORE")},
            recipes=[
                RecipeSpec(
                    output="STEEL",
                    output_quantity=10,
                    inputs={"MISSING_RESOURCE": 15},  # Not defined
                    energy_kwh=100,
                    time_hours=2.0
                )
            ],
            modules={},
            initial_state={},
            constraints={},
            subsystems={}
        )

        validator = SpecValidator()
        with pytest.raises(SpecValidationError) as exc_info:
            validator.validate(spec)

        assert "MISSING_RESOURCE" in str(exc_info.value)

    def test_validate_missing_module(self):
        """Test validation fails for missing module"""
        spec = FactorySpec(
            metadata={},
            resources={
                "IRON_ORE": ResourceSpec(name="IRON_ORE"),
                "STEEL": ResourceSpec(name="STEEL")
            },
            recipes=[
                RecipeSpec(
                    output="STEEL",
                    output_quantity=10,
                    inputs={"IRON_ORE": 15},
                    energy_kwh=100,
                    time_hours=2.0,
                    required_module="nonexistent_module"  # Not defined
                )
            ],
            modules={},
            initial_state={},
            constraints={},
            subsystems={}
        )

        validator = SpecValidator()
        with pytest.raises(SpecValidationError) as exc_info:
            validator.validate(spec)

        assert "nonexistent_module" in str(exc_info.value)

    def test_validate_circular_dependency(self, spec_with_circular_dependency):
        """Test validation detects circular dependencies"""
        loader = SpecLoader()

        with pytest.raises(CircularDependencyError) as exc_info:
            loader.load_spec(spec_with_circular_dependency)

        error = exc_info.value
        assert len(error.cycle) > 0
        # Cycle should contain the circular references
        assert any(item in error.cycle for item in ["A", "B", "C"])

    def test_validate_invalid_module_throughput(self):
        """Test validation fails for invalid module throughput"""
        spec = FactorySpec(
            metadata={},
            resources={},
            recipes=[],
            modules={
                "bad_module": ModuleSpecData(
                    module_type="bad_module",
                    max_throughput=-10.0,  # Invalid: negative
                    power_consumption_idle=10.0,
                    power_consumption_active=100.0
                )
            },
            initial_state={},
            constraints={},
            subsystems={}
        )

        validator = SpecValidator()
        with pytest.raises(SpecValidationError) as exc_info:
            validator.validate(spec)

        assert "throughput" in str(exc_info.value).lower()


class TestSpecRegistry:
    """Test SpecRegistry class"""

    def test_registry_creation(self, temp_spec_dir):
        """Test creating a spec registry"""
        registry = SpecRegistry(spec_dir=str(temp_spec_dir))
        assert registry.spec_dir == str(temp_spec_dir)

    def test_list_specs(self, temp_spec_dir, minimal_spec_file):
        """Test listing available specs"""
        registry = SpecRegistry(spec_dir=str(temp_spec_dir))
        specs = registry.list_specs()

        assert len(specs) > 0
        assert any("test_minimal" in spec for spec in specs)


class TestSpecInheritance:
    """Test spec inheritance functionality"""

    def test_spec_inheritance_basic(self, temp_spec_dir):
        """Test basic spec inheritance"""
        # Create parent spec
        parent_data = {
            "metadata": {"name": "Parent"},
            "resources": {
                "IRON_ORE": {"density": 4.0},
                "STEEL": {"density": 7.8}
            },
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {"param1": 100}
        }

        parent_path = temp_spec_dir / "parent.json"
        with open(parent_path, 'w') as f:
            json.dump(parent_data, f)

        # Create child spec
        child_data = {
            "metadata": {
                "name": "Child",
                "parent": str(parent_path)
            },
            "resources": {
                "ALUMINUM": {"density": 2.7}  # Add new resource
            },
            "constraints": {"param1": 200}  # Override
        }

        child_path = temp_spec_dir / "child.json"
        with open(child_path, 'w') as f:
            json.dump(child_data, f)

        # Load child spec
        loader = SpecLoader()
        child_spec = loader.load_spec(str(child_path))

        # Check inheritance
        assert child_spec.metadata["name"] == "Child"
        assert "IRON_ORE" in child_spec.resources  # From parent
        assert "STEEL" in child_spec.resources  # From parent
        assert "ALUMINUM" in child_spec.resources  # From child
        assert child_spec.constraints["param1"] == 200  # Overridden


if __name__ == "__main__":
    pytest.main([__file__, "-v"])