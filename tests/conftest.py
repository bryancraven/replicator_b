#!/usr/bin/env python3
"""
Pytest configuration and fixtures for factory simulation tests
"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any
from enum import Enum

# Import modules under test
from modular_framework import (
    EventBus,
    SubsystemConfig,
    SimulationContext,
    SubsystemOrchestrator,
    MockSubsystem,
)
from spec_loader import SpecLoader, FactorySpec, ResourceSpec, RecipeSpec, ModuleSpecData


# ===============================================================================
# SESSION FIXTURES
# ===============================================================================

@pytest.fixture(scope="session")
def temp_spec_dir(tmp_path_factory):
    """Create a temporary directory for spec files"""
    return tmp_path_factory.mktemp("specs")


# ===============================================================================
# FRAMEWORK FIXTURES
# ===============================================================================

@pytest.fixture
def event_bus():
    """Create a fresh event bus for testing"""
    return EventBus(max_history=100)


@pytest.fixture
def subsystem_config():
    """Create a basic subsystem configuration"""
    return SubsystemConfig({
        "enabled": True,
        "param1": 100,
        "param2": "test_value"
    })


@pytest.fixture
def simulation_context():
    """Create a basic simulation context"""
    return SimulationContext(
        time=0.0,
        delta_time=0.1,
        resources={"STEEL": 1000, "IRON_ORE": 500},
        modules={"cnc": {"count": 1, "status": "idle"}},
        tasks=[],
        metrics={}
    )


@pytest.fixture
def orchestrator(event_bus):
    """Create an orchestrator with event bus"""
    return SubsystemOrchestrator(event_bus)


@pytest.fixture
def mock_subsystem(subsystem_config, event_bus):
    """Create an initialized mock subsystem"""
    subsystem = MockSubsystem("test_mock", update_return={"status": "ok"})
    subsystem.initialize(subsystem_config, event_bus)
    return subsystem


# ===============================================================================
# SPEC FIXTURES
# ===============================================================================

@pytest.fixture
def minimal_resource_spec():
    """Create a minimal resource specification"""
    return {
        "IRON_ORE": ResourceSpec(
            name="IRON_ORE",
            density=4.0,
            storage_temp=25.0,
            contamination_sensitivity=0.1,
            hazardous=False,
            recyclable=True
        ),
        "STEEL": ResourceSpec(
            name="STEEL",
            density=7.8,
            storage_temp=25.0,
            contamination_sensitivity=0.2,
            hazardous=False,
            recyclable=True
        ),
        "STEEL_BEAM": ResourceSpec(
            name="STEEL_BEAM",
            density=7.8,
            storage_temp=25.0,
            contamination_sensitivity=0.2,
            hazardous=False,
            recyclable=True
        )
    }


@pytest.fixture
def minimal_recipe_specs():
    """Create minimal recipe specifications"""
    return [
        RecipeSpec(
            output="STEEL",
            output_quantity=10,
            inputs={"IRON_ORE": 15},
            energy_kwh=100,
            time_hours=2.0,
            required_module="smelter"
        ),
        RecipeSpec(
            output="STEEL_BEAM",
            output_quantity=1,
            inputs={"STEEL": 10},
            energy_kwh=50,
            time_hours=1.0,
            required_module="cnc"
        )
    ]


@pytest.fixture
def minimal_module_specs():
    """Create minimal module specifications"""
    return {
        "smelter": ModuleSpecData(
            module_type="smelter",
            max_throughput=100.0,
            power_consumption_idle=10.0,
            power_consumption_active=100.0,
            mtbf_hours=5000,
            maintenance_interval=500,
            degradation_rate=0.02
        ),
        "cnc": ModuleSpecData(
            module_type="cnc",
            max_throughput=50.0,
            power_consumption_idle=5.0,
            power_consumption_active=50.0,
            mtbf_hours=3000,
            maintenance_interval=300,
            degradation_rate=0.03
        )
    }


@pytest.fixture
def minimal_factory_spec(minimal_resource_spec, minimal_recipe_specs, minimal_module_specs):
    """Create a complete minimal factory spec"""
    return FactorySpec(
        metadata={
            "name": "Minimal Test Factory",
            "version": "1.0.0",
            "description": "Minimal factory for testing"
        },
        resources=minimal_resource_spec,
        recipes=minimal_recipe_specs,
        modules=minimal_module_specs,
        initial_state={
            "modules": {"smelter": 1, "cnc": 1},
            "resources": {"IRON_ORE": 1000},
            "energy_kwh": 10000
        },
        constraints={
            "enable_capacity_limits": True,
            "parallel_processing_limit": 5
        },
        subsystems={}
    )


@pytest.fixture
def minimal_spec_file(temp_spec_dir, minimal_resource_spec):
    """Create a minimal spec file on disk"""
    spec_data = {
        "metadata": {
            "name": "Test Factory",
            "version": "1.0.0"
        },
        "resources": {
            "IRON_ORE": {
                "density": 4.0,
                "storage_temp": 25.0,
                "contamination_sensitivity": 0.1
            },
            "STEEL": {
                "density": 7.8,
                "storage_temp": 25.0,
                "contamination_sensitivity": 0.2
            }
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
        "initial_state": {
            "modules": {"smelter": 1},
            "resources": {"IRON_ORE": 1000}
        },
        "constraints": {}
    }

    spec_path = temp_spec_dir / "test_minimal.json"
    with open(spec_path, 'w') as f:
        json.dump(spec_data, f, indent=2)

    return str(spec_path)


@pytest.fixture
def spec_with_circular_dependency(temp_spec_dir):
    """Create a spec with circular dependency for testing validation"""
    spec_data = {
        "metadata": {"name": "Circular Test"},
        "resources": {
            "A": {"density": 1.0},
            "B": {"density": 1.0},
            "C": {"density": 1.0}
        },
        "recipes": [
            {
                "output": "A",
                "output_quantity": 1,
                "inputs": {"C": 1},
                "energy_kwh": 10,
                "time_hours": 1.0
            },
            {
                "output": "B",
                "output_quantity": 1,
                "inputs": {"A": 1},
                "energy_kwh": 10,
                "time_hours": 1.0
            },
            {
                "output": "C",
                "output_quantity": 1,
                "inputs": {"B": 1},
                "energy_kwh": 10,
                "time_hours": 1.0
            }
        ],
        "modules": {},
        "initial_state": {},
        "constraints": {}
    }

    spec_path = temp_spec_dir / "circular.json"
    with open(spec_path, 'w') as f:
        json.dump(spec_data, f, indent=2)

    return str(spec_path)


# ===============================================================================
# HELPER FIXTURES
# ===============================================================================

@pytest.fixture
def simple_resource_enum():
    """Create a simple ResourceType enum for testing"""
    return Enum('ResourceType', {
        'IRON_ORE': 'iron_ore',
        'STEEL': 'steel',
        'STEEL_BEAM': 'steel_beam'
    })


# ===============================================================================
# PYTEST CONFIGURATION
# ===============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# ===============================================================================
# ASSERTION HELPERS
# ===============================================================================

class AssertionHelpers:
    """Helper methods for common assertions"""

    @staticmethod
    def assert_event_published(event_bus: EventBus, event_type, source=None):
        """Assert that an event of given type was published"""
        history = event_bus.get_history(event_type=event_type, source=source)
        assert len(history) > 0, f"No events of type {event_type} found"

    @staticmethod
    def assert_subsystem_metrics(subsystem, expected_metrics: Dict[str, Any]):
        """Assert that subsystem has expected metrics"""
        actual = subsystem.get_metrics()
        for key, expected_value in expected_metrics.items():
            assert key in actual, f"Metric '{key}' not found in subsystem metrics"
            assert actual[key] == expected_value, \
                f"Metric '{key}': expected {expected_value}, got {actual[key]}"


@pytest.fixture
def assert_helpers():
    """Provide assertion helper methods"""
    return AssertionHelpers()