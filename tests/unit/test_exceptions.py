#!/usr/bin/env python3
"""
Unit tests for custom exceptions module
"""

import pytest
from exceptions import (
    FactorySimulationError,
    SpecError,
    SpecValidationError,
    SpecNotFoundError,
    SpecParseError,
    CircularDependencyError,
    ResourceError,
    ResourceNotFoundError,
    InsufficientResourcesError,
    StorageCapacityError,
    SubsystemError,
    SubsystemNotFoundError,
    SubsystemConfigError,
    ModuleError,
    ModuleNotFoundError,
    TaskError,
    TaskValidationError,
    ConfigurationError,
    InvalidConfigurationError,
    SimulationError,
    SimulationDeadlockError,
)


class TestBaseExceptions:
    """Test base exception hierarchy"""

    def test_factory_simulation_error_is_base(self):
        """Test that FactorySimulationError is the base exception"""
        error = FactorySimulationError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_spec_error_inherits_from_base(self):
        """Test that SpecError inherits from FactorySimulationError"""
        error = SpecError("spec error")
        assert isinstance(error, FactorySimulationError)
        assert isinstance(error, Exception)


class TestSpecExceptions:
    """Test spec-related exceptions"""

    def test_spec_validation_error_with_single_error(self):
        """Test SpecValidationError with single error"""
        error = SpecValidationError("Validation failed", ["Missing resource 'STEEL'"])
        assert "Validation failed" in str(error)
        assert "Missing resource 'STEEL'" in str(error)
        assert len(error.errors) == 1

    def test_spec_validation_error_with_multiple_errors(self):
        """Test SpecValidationError with multiple errors"""
        errors = ["Error 1", "Error 2", "Error 3"]
        error = SpecValidationError("Multiple errors", errors)
        assert len(error.errors) == 3
        for err in errors:
            assert err in str(error)

    def test_spec_not_found_error(self):
        """Test SpecNotFoundError"""
        error = SpecNotFoundError("/path/to/missing.spec")
        assert error.spec_path == "/path/to/missing.spec"
        assert "not found" in str(error).lower()

    def test_spec_parse_error(self):
        """Test SpecParseError"""
        error = SpecParseError("test.yaml", "Invalid YAML syntax")
        assert error.spec_path == "test.yaml"
        assert error.reason == "Invalid YAML syntax"
        assert "test.yaml" in str(error)
        assert "Invalid YAML syntax" in str(error)

    def test_circular_dependency_error(self):
        """Test CircularDependencyError"""
        cycle = ["STEEL", "IRON_ORE", "MINING_MODULE", "STEEL"]
        error = CircularDependencyError(cycle)
        assert error.cycle == cycle
        assert "STEEL" in str(error)
        assert "circular" in str(error).lower()


class TestResourceExceptions:
    """Test resource-related exceptions"""

    def test_resource_not_found_error_without_context(self):
        """Test ResourceNotFoundError without context"""
        error = ResourceNotFoundError("UNOBTANIUM")
        assert error.resource_name == "UNOBTANIUM"
        assert error.context is None
        assert "UNOBTANIUM" in str(error)

    def test_resource_not_found_error_with_context(self):
        """Test ResourceNotFoundError with context"""
        error = ResourceNotFoundError("STEEL", "recipe for BEAM")
        assert error.resource_name == "STEEL"
        assert error.context == "recipe for BEAM"
        assert "STEEL" in str(error)
        assert "recipe for BEAM" in str(error)

    def test_insufficient_resources_error(self):
        """Test InsufficientResourcesError"""
        error = InsufficientResourcesError("IRON_ORE", required=100.0, available=50.0)
        assert error.resource_name == "IRON_ORE"
        assert error.required == 100.0
        assert error.available == 50.0
        assert "100" in str(error)
        assert "50" in str(error)

    def test_storage_capacity_error(self):
        """Test StorageCapacityError"""
        error = StorageCapacityError("volume", required=1500.0, capacity=1000.0)
        assert error.constraint == "volume"
        assert error.required == 1500.0
        assert error.capacity == 1000.0
        assert "volume" in str(error)


class TestSubsystemExceptions:
    """Test subsystem-related exceptions"""

    def test_subsystem_config_error(self):
        """Test SubsystemConfigError"""
        error = SubsystemConfigError("transport", "Invalid AGV fleet size: -5")
        assert error.subsystem_name == "transport"
        assert error.reason == "Invalid AGV fleet size: -5"
        assert "transport" in str(error)
        assert "AGV" in str(error)

    def test_subsystem_not_found_error_without_available(self):
        """Test SubsystemNotFoundError without available list"""
        error = SubsystemNotFoundError("quantum_transport")
        assert error.subsystem_name == "quantum_transport"
        assert error.available == []
        assert "quantum_transport" in str(error)

    def test_subsystem_not_found_error_with_available(self):
        """Test SubsystemNotFoundError with available list"""
        available = ["transport_wrapper", "genetic_routing", "swarm_transport"]
        error = SubsystemNotFoundError("quantum_transport", available)
        assert error.subsystem_name == "quantum_transport"
        assert error.available == available
        assert "transport_wrapper" in str(error)


class TestModuleExceptions:
    """Test module-related exceptions"""

    def test_module_not_found_error(self):
        """Test ModuleNotFoundError"""
        error = ModuleNotFoundError("quantum_assembler")
        assert error.module_type == "quantum_assembler"
        assert "quantum_assembler" in str(error)

    def test_module_not_found_error_with_context(self):
        """Test ModuleNotFoundError with context"""
        error = ModuleNotFoundError("cnc", "STEEL_BEAM production")
        assert error.module_type == "cnc"
        assert error.context == "STEEL_BEAM production"
        assert "cnc" in str(error)
        assert "STEEL_BEAM" in str(error)


class TestTaskExceptions:
    """Test task-related exceptions"""

    def test_task_validation_error(self):
        """Test TaskValidationError"""
        error = TaskValidationError("task_00042", "Missing required input resources")
        assert error.task_id == "task_00042"
        assert error.reason == "Missing required input resources"
        assert "task_00042" in str(error)

    def test_task_blocked_error_without_dependencies(self):
        """Test TaskBlockedError without dependencies"""
        error = TaskBlockedError("task_00100", "Waiting for module availability")
        assert error.task_id == "task_00100"
        assert error.blocking_reason == "Waiting for module availability"
        assert error.dependencies == []

    def test_task_blocked_error_with_dependencies(self):
        """Test TaskBlockedError with dependencies"""
        deps = ["task_00050", "task_00051"]
        error = TaskBlockedError("task_00100", "Blocked by dependencies", deps)
        assert error.dependencies == deps
        assert "task_00050" in str(error)


class TestConfigurationExceptions:
    """Test configuration-related exceptions"""

    def test_invalid_configuration_error(self):
        """Test InvalidConfigurationError"""
        error = InvalidConfigurationError(
            "parallel_processing_limit",
            -5,
            "Must be positive"
        )
        assert error.parameter == "parallel_processing_limit"
        assert error.value == -5
        assert error.reason == "Must be positive"

    def test_missing_configuration_error(self):
        """Test MissingConfigurationError"""
        error = InvalidConfigurationError(
            "solar_capacity_kw",
            None,
            "Required parameter"
        )
        assert "solar_capacity_kw" in str(error)


class TestSimulationExceptions:
    """Test simulation-related exceptions"""

    def test_simulation_deadlock_error(self):
        """Test SimulationDeadlockError"""
        error = SimulationDeadlockError(
            blocked_tasks=42,
            reason="All tasks waiting for unavailable resources"
        )
        assert error.blocked_tasks == 42
        assert "42" in str(error)
        assert "deadlock" in str(error).lower()


class TestExceptionInheritance:
    """Test exception inheritance hierarchy"""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from FactorySimulationError"""
        exception_classes = [
            SpecError,
            ResourceError,
            SubsystemError,
            ModuleError,
            TaskError,
            ConfigurationError,
            SimulationError,
        ]

        for exc_class in exception_classes:
            error = exc_class("test")
            assert isinstance(error, FactorySimulationError)
            assert isinstance(error, Exception)

    def test_specific_exceptions_inherit_from_category(self):
        """Test that specific exceptions inherit from their category"""
        test_cases = [
            (SpecValidationError("test", []), SpecError),
            (ResourceNotFoundError("test"), ResourceError),
            (SubsystemConfigError("test", "reason"), SubsystemError),
            (ModuleNotFoundError("test"), ModuleError),
            (TaskValidationError("test", "reason"), TaskError),
        ]

        for error, parent_class in test_cases:
            assert isinstance(error, parent_class)
            assert isinstance(error, FactorySimulationError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])