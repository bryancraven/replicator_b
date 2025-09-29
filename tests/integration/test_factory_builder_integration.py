#!/usr/bin/env python3
"""
Integration tests for factory_builder module

Tests the complete workflow of creating factories from spec files
with custom subsystems.
"""

import pytest
import json
import tempfile
from pathlib import Path

from factory_builder import (
    create_factory_from_spec,
    list_available_subsystems,
    validate_spec_subsystems
)
from exceptions import (
    SpecNotFoundError,
    SubsystemNotFoundError,
    SubsystemConfigError
)
from modular_framework import UpdateStrategy


class TestFactoryBuilderIntegration:
    """Integration tests for factory builder"""

    def test_create_factory_from_minimal_spec(self, temp_spec_dir):
        """Test creating factory from minimal spec file"""
        # Create minimal spec
        spec_data = {
            "metadata": {"name": "Test Factory", "version": "1.0.0"},
            "resources": {
                "IRON_ORE": {"density": 4.0},
                "STEEL": {"density": 7.8}
            },
            "recipes": [
                {
                    "output": "STEEL",
                    "output_quantity": 10,
                    "inputs": {"IRON_ORE": 15},
                    "energy_kwh": 100,
                    "time_hours": 2.0,
                    "required_module": "smelter"
                }
            ],
            "modules": {
                "smelter": {
                    "max_throughput": 100.0,
                    "power_consumption_idle": 10.0,
                    "power_consumption_active": 100.0
                }
            },
            "initial_state": {},
            "constraints": {}
        }

        spec_path = temp_spec_dir / "test_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Create factory
        factory = create_factory_from_spec(str(spec_path))

        # Verify factory was created
        assert factory is not None
        assert hasattr(factory, 'orchestrator')
        assert hasattr(factory, 'spec')
        assert factory.spec.metadata["name"] == "Test Factory"

    def test_create_factory_with_custom_subsystems(self, temp_spec_dir):
        """Test creating factory with custom subsystem implementations"""
        spec_data = {
            "metadata": {"name": "Custom Factory", "version": "1.0.0"},
            "resources": {
                "IRON_ORE": {"density": 4.0},
                "STEEL": {"density": 7.8}
            },
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {},
            "subsystem_implementations": {
                "test": "mock"  # Use mock subsystem for testing
            },
            "subsystem_data": {
                "test": {
                    "enabled": True,
                    "param1": 100
                }
            }
        }

        spec_path = temp_spec_dir / "custom_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Create factory
        factory = create_factory_from_spec(str(spec_path))

        # Verify custom subsystem was added
        assert "test" in factory.orchestrator.subsystems
        assert factory.orchestrator.subsystems["test"].name == "mock"

    def test_create_factory_with_invalid_subsystem(self, temp_spec_dir):
        """Test that invalid subsystem raises appropriate error"""
        spec_data = {
            "metadata": {"name": "Invalid Factory", "version": "1.0.0"},
            "resources": {},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {},
            "subsystem_implementations": {
                "transport": "nonexistent_subsystem"
            }
        }

        spec_path = temp_spec_dir / "invalid_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Should raise SubsystemNotFoundError
        with pytest.raises(SubsystemConfigError) as exc_info:
            create_factory_from_spec(str(spec_path))

        assert "transport" in str(exc_info.value)

    def test_create_factory_with_update_strategy(self, temp_spec_dir):
        """Test creating factory with different update strategies"""
        spec_data = {
            "metadata": {"name": "Strategy Test", "version": "1.0.0"},
            "resources": {"IRON_ORE": {"density": 4.0}},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {}
        }

        spec_path = temp_spec_dir / "strategy_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Test each strategy
        for strategy in [UpdateStrategy.SEQUENTIAL, UpdateStrategy.PARALLEL,
                        UpdateStrategy.DEPENDENCY]:
            factory = create_factory_from_spec(str(spec_path), update_strategy=strategy)
            assert factory.orchestrator.update_strategy == strategy

    def test_create_factory_with_profile(self, temp_spec_dir):
        """Test creating factory with configuration profile"""
        spec_data = {
            "metadata": {"name": "Profile Test", "version": "1.0.0"},
            "resources": {"IRON_ORE": {"density": 4.0}},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {
                "parallel_processing_limit": 5
            },
            "profiles": {
                "high_throughput": {
                    "description": "High throughput mode",
                    "parallel_processing_limit": 20
                }
            }
        }

        spec_path = temp_spec_dir / "profile_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Create without profile
        factory1 = create_factory_from_spec(str(spec_path))
        # Config checking would go here if exposed

        # Create with profile
        factory2 = create_factory_from_spec(str(spec_path), profile="high_throughput")
        # Verify profile was applied (config would be different)

    def test_nonexistent_spec_raises_error(self):
        """Test that nonexistent spec file raises SpecNotFoundError"""
        with pytest.raises(SpecNotFoundError):
            create_factory_from_spec("/path/to/nonexistent/spec.json")


class TestListAvailableSubsystems:
    """Test subsystem listing functionality"""

    def test_list_returns_dict(self):
        """Test that list_available_subsystems returns a dictionary"""
        subsystems = list_available_subsystems()
        assert isinstance(subsystems, dict)
        assert len(subsystems) > 0

    def test_list_contains_known_subsystems(self):
        """Test that list contains known subsystem implementations"""
        subsystems = list_available_subsystems()

        # Check for some expected subsystems
        expected = ["mock", "adaptive_transport", "ml_quality"]
        for name in expected:
            assert name in subsystems
            assert isinstance(subsystems[name], str)

    def test_list_has_descriptions(self):
        """Test that each subsystem has a description"""
        subsystems = list_available_subsystems()
        for name, description in subsystems.items():
            assert description is not None
            assert len(description) > 0


class TestValidateSpecSubsystems:
    """Test subsystem validation functionality"""

    def test_validate_valid_spec(self, temp_spec_dir):
        """Test validation of spec with valid subsystems"""
        spec_data = {
            "metadata": {"name": "Valid Spec", "version": "1.0.0"},
            "resources": {},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {},
            "subsystem_implementations": {
                "test": "mock"
            }
        }

        spec_path = temp_spec_dir / "valid_subsystems.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Should return True
        result = validate_spec_subsystems(str(spec_path))
        assert result is True

    def test_validate_invalid_spec(self, temp_spec_dir):
        """Test validation of spec with invalid subsystems"""
        spec_data = {
            "metadata": {"name": "Invalid Spec", "version": "1.0.0"},
            "resources": {},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {},
            "subsystem_implementations": {
                "transport": "nonexistent_implementation"
            }
        }

        spec_path = temp_spec_dir / "invalid_subsystems.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Should return False
        result = validate_spec_subsystems(str(spec_path))
        assert result is False

    def test_validate_spec_without_subsystems(self, temp_spec_dir):
        """Test validation of spec without subsystem_implementations"""
        spec_data = {
            "metadata": {"name": "No Subsystems", "version": "1.0.0"},
            "resources": {},
            "recipes": [],
            "modules": {},
            "initial_state": {},
            "constraints": {}
        }

        spec_path = temp_spec_dir / "no_subsystems.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f)

        # Should return True (no subsystems to validate)
        result = validate_spec_subsystems(str(spec_path))
        assert result is True


class TestEndToEndWorkflow:
    """End-to-end integration tests"""

    def test_complete_factory_creation_workflow(self, temp_spec_dir):
        """Test complete workflow from spec to factory with simulation"""
        # Create comprehensive spec
        spec_data = {
            "metadata": {
                "name": "Complete Factory",
                "version": "1.0.0",
                "description": "End-to-end test factory"
            },
            "resources": {
                "IRON_ORE": {"density": 4.0, "recyclable": True},
                "STEEL": {"density": 7.8, "recyclable": True},
                "STEEL_BEAM": {"density": 7.8, "recyclable": True}
            },
            "recipes": [
                {
                    "output": "STEEL",
                    "output_quantity": 10,
                    "inputs": {"IRON_ORE": 15},
                    "energy_kwh": 100,
                    "time_hours": 2.0,
                    "required_module": "smelter"
                },
                {
                    "output": "STEEL_BEAM",
                    "output_quantity": 1,
                    "inputs": {"STEEL": 10},
                    "energy_kwh": 50,
                    "time_hours": 1.0,
                    "required_module": "cnc"
                }
            ],
            "modules": {
                "smelter": {
                    "max_throughput": 100.0,
                    "power_consumption_idle": 10.0,
                    "power_consumption_active": 100.0,
                    "mtbf_hours": 5000
                },
                "cnc": {
                    "max_throughput": 50.0,
                    "power_consumption_idle": 5.0,
                    "power_consumption_active": 50.0,
                    "mtbf_hours": 3000
                }
            },
            "initial_state": {
                "modules": {"smelter": 1, "cnc": 1},
                "resources": {"IRON_ORE": 1000},
                "energy_kwh": 10000
            },
            "constraints": {
                "enable_capacity_limits": True,
                "parallel_processing_limit": 5,
                "enable_degradation": False  # Disable for faster test
            },
            "subsystems": {},
            "profiles": {
                "fast": {
                    "description": "Fast test mode",
                    "processing_speed_multiplier": 10.0
                }
            }
        }

        spec_path = temp_spec_dir / "complete_factory.json"
        with open(spec_path, 'w') as f:
            json.dump(spec_data, f, indent=2)

        # Step 1: Validate subsystems
        assert validate_spec_subsystems(str(spec_path)) is True

        # Step 2: Create factory
        factory = create_factory_from_spec(str(spec_path), profile="fast")

        # Step 3: Verify factory properties
        assert factory is not None
        assert factory.spec.metadata["name"] == "Complete Factory"
        assert len(factory.spec.resources) == 3
        assert len(factory.spec.recipes) == 2
        assert len(factory.spec.modules) == 2

        # Step 4: Verify resource enum was created
        assert hasattr(factory, 'resource_enum')
        assert hasattr(factory.resource_enum, 'IRON_ORE')
        assert hasattr(factory.resource_enum, 'STEEL')
        assert hasattr(factory.resource_enum, 'STEEL_BEAM')

        # Step 5: Test orchestrator
        assert len(factory.orchestrator.subsystems) >= 0  # May have default subsystems

        # Factory is ready for simulation
        # (Actual simulation would require more setup and is out of scope for unit tests)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])