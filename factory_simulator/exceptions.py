#!/usr/bin/env python3
"""
Custom exceptions for the Self-Replicating Factory Simulation

This module defines all custom exception types used throughout the simulation,
providing clear error messages and context for debugging.
"""

from typing import Optional, List, Any


# ===============================================================================
# BASE EXCEPTIONS
# ===============================================================================

class FactorySimulationError(Exception):
    """Base exception for all factory simulation errors"""
    pass


# ===============================================================================
# SPEC SYSTEM EXCEPTIONS
# ===============================================================================

class SpecError(FactorySimulationError):
    """Base exception for spec-related errors"""
    pass


class SpecValidationError(SpecError):
    """Raised when a spec file fails validation"""

    def __init__(self, message: str, errors: Optional[List[str]] = None):
        """
        Initialize spec validation error

        Args:
            message: Human-readable error message
            errors: List of specific validation errors
        """
        self.errors = errors or []
        error_detail = "\n".join(f"  - {err}" for err in self.errors) if self.errors else ""
        full_message = f"{message}\n{error_detail}" if error_detail else message
        super().__init__(full_message)


class SpecNotFoundError(SpecError):
    """Raised when a spec file cannot be found"""

    def __init__(self, spec_path: str):
        self.spec_path = spec_path
        super().__init__(f"Spec file not found: {spec_path}")


class SpecParseError(SpecError):
    """Raised when a spec file cannot be parsed"""

    def __init__(self, spec_path: str, reason: str):
        self.spec_path = spec_path
        self.reason = reason
        super().__init__(f"Failed to parse spec file '{spec_path}': {reason}")


class SpecInheritanceError(SpecError):
    """Raised when spec inheritance fails"""

    def __init__(self, child_spec: str, parent_spec: str, reason: str):
        self.child_spec = child_spec
        self.parent_spec = parent_spec
        self.reason = reason
        super().__init__(
            f"Spec inheritance failed: '{child_spec}' cannot inherit from '{parent_spec}': {reason}"
        )


class CircularDependencyError(SpecValidationError):
    """Raised when circular dependencies are detected in recipes"""

    def __init__(self, cycle: List[str]):
        self.cycle = cycle
        cycle_str = " -> ".join(cycle)
        super().__init__(
            f"Circular dependency detected in recipe graph: {cycle_str}",
            [f"Cycle: {cycle_str}"]
        )


# ===============================================================================
# RESOURCE EXCEPTIONS
# ===============================================================================

class ResourceError(FactorySimulationError):
    """Base exception for resource-related errors"""
    pass


class ResourceNotFoundError(ResourceError):
    """Raised when a required resource is not found"""

    def __init__(self, resource_name: str, context: Optional[str] = None):
        self.resource_name = resource_name
        self.context = context
        message = f"Resource '{resource_name}' not found"
        if context:
            message += f" in {context}"
        super().__init__(message)


class InsufficientResourcesError(ResourceError):
    """Raised when there are insufficient resources for an operation"""

    def __init__(self, resource_name: str, required: float, available: float):
        self.resource_name = resource_name
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient {resource_name}: required {required:.2f}, available {available:.2f}"
        )


class StorageCapacityError(ResourceError):
    """Raised when storage capacity is exceeded"""

    def __init__(self, constraint: str, required: float, capacity: float):
        self.constraint = constraint
        self.required = required
        self.capacity = capacity
        super().__init__(
            f"Storage capacity exceeded ({constraint}): "
            f"required {required:.2f}, capacity {capacity:.2f}"
        )


# ===============================================================================
# SUBSYSTEM EXCEPTIONS
# ===============================================================================

class SubsystemError(FactorySimulationError):
    """Base exception for subsystem-related errors"""
    pass


class SubsystemConfigError(SubsystemError):
    """Raised when subsystem configuration is invalid"""

    def __init__(self, subsystem_name: str, reason: str):
        self.subsystem_name = subsystem_name
        self.reason = reason
        super().__init__(f"Invalid configuration for subsystem '{subsystem_name}': {reason}")


class SubsystemNotFoundError(SubsystemError):
    """Raised when a subsystem implementation is not found"""

    def __init__(self, subsystem_name: str, available: Optional[List[str]] = None):
        self.subsystem_name = subsystem_name
        self.available = available or []
        message = f"Subsystem implementation '{subsystem_name}' not found"
        if self.available:
            message += f"\nAvailable implementations: {', '.join(sorted(self.available))}"
        super().__init__(message)


class SubsystemInitializationError(SubsystemError):
    """Raised when subsystem initialization fails"""

    def __init__(self, subsystem_name: str, reason: str):
        self.subsystem_name = subsystem_name
        self.reason = reason
        super().__init__(f"Failed to initialize subsystem '{subsystem_name}': {reason}")


class SubsystemValidationError(SubsystemError):
    """Raised when subsystem validation fails"""

    def __init__(self, subsystem_name: str, errors: List[str]):
        self.subsystem_name = subsystem_name
        self.errors = errors
        error_detail = "\n".join(f"  - {err}" for err in errors)
        super().__init__(
            f"Subsystem '{subsystem_name}' validation failed:\n{error_detail}"
        )


# ===============================================================================
# MODULE EXCEPTIONS
# ===============================================================================

class ModuleError(FactorySimulationError):
    """Base exception for module-related errors"""
    pass


class ModuleNotFoundError(ModuleError):
    """Raised when a required module is not available"""

    def __init__(self, module_type: str, context: Optional[str] = None):
        self.module_type = module_type
        self.context = context
        message = f"Module type '{module_type}' not found"
        if context:
            message += f" for {context}"
        super().__init__(message)


class ModuleCapacityError(ModuleError):
    """Raised when module capacity is exceeded"""

    def __init__(self, module_type: str, current_load: int, max_capacity: int):
        self.module_type = module_type
        self.current_load = current_load
        self.max_capacity = max_capacity
        super().__init__(
            f"Module '{module_type}' capacity exceeded: "
            f"current load {current_load}, max capacity {max_capacity}"
        )


class ModuleFailureError(ModuleError):
    """Raised when a module fails during operation"""

    def __init__(self, module_type: str, reason: str):
        self.module_type = module_type
        self.reason = reason
        super().__init__(f"Module '{module_type}' failed: {reason}")


# ===============================================================================
# TASK EXCEPTIONS
# ===============================================================================

class TaskError(FactorySimulationError):
    """Base exception for task-related errors"""
    pass


class TaskValidationError(TaskError):
    """Raised when task validation fails"""

    def __init__(self, task_id: str, reason: str):
        self.task_id = task_id
        self.reason = reason
        super().__init__(f"Task '{task_id}' validation failed: {reason}")


class TaskExecutionError(TaskError):
    """Raised when task execution fails"""

    def __init__(self, task_id: str, reason: str, recoverable: bool = False):
        self.task_id = task_id
        self.reason = reason
        self.recoverable = recoverable
        recovery_note = " (recoverable)" if recoverable else ""
        super().__init__(f"Task '{task_id}' execution failed{recovery_note}: {reason}")


class TaskBlockedError(TaskError):
    """Raised when a task is blocked and cannot proceed"""

    def __init__(self, task_id: str, blocking_reason: str, dependencies: Optional[List[str]] = None):
        self.task_id = task_id
        self.blocking_reason = blocking_reason
        self.dependencies = dependencies or []
        message = f"Task '{task_id}' is blocked: {blocking_reason}"
        if self.dependencies:
            message += f"\nBlocked by: {', '.join(self.dependencies)}"
        super().__init__(message)


# ===============================================================================
# CONFIGURATION EXCEPTIONS
# ===============================================================================

class ConfigurationError(FactorySimulationError):
    """Base exception for configuration errors"""
    pass


class InvalidConfigurationError(ConfigurationError):
    """Raised when configuration is invalid"""

    def __init__(self, parameter: str, value: Any, reason: str):
        self.parameter = parameter
        self.value = value
        self.reason = reason
        super().__init__(
            f"Invalid configuration for '{parameter}' = {value}: {reason}"
        )


class MissingConfigurationError(ConfigurationError):
    """Raised when required configuration is missing"""

    def __init__(self, parameter: str, context: Optional[str] = None):
        self.parameter = parameter
        self.context = context
        message = f"Required configuration parameter '{parameter}' is missing"
        if context:
            message += f" for {context}"
        super().__init__(message)


class ConfigurationConflictError(ConfigurationError):
    """Raised when configurations conflict"""

    def __init__(self, param1: str, param2: str, reason: str):
        self.param1 = param1
        self.param2 = param2
        self.reason = reason
        super().__init__(
            f"Configuration conflict between '{param1}' and '{param2}': {reason}"
        )


# ===============================================================================
# SIMULATION EXCEPTIONS
# ===============================================================================

class SimulationError(FactorySimulationError):
    """Base exception for simulation runtime errors"""
    pass


class SimulationStateError(SimulationError):
    """Raised when simulation state is invalid"""

    def __init__(self, reason: str, current_state: Optional[str] = None):
        self.reason = reason
        self.current_state = current_state
        message = f"Invalid simulation state: {reason}"
        if current_state:
            message += f" (current state: {current_state})"
        super().__init__(message)


class SimulationTimeoutError(SimulationError):
    """Raised when simulation exceeds time limits"""

    def __init__(self, elapsed_time: float, max_time: float):
        self.elapsed_time = elapsed_time
        self.max_time = max_time
        super().__init__(
            f"Simulation timeout: elapsed {elapsed_time:.1f}h, max {max_time:.1f}h"
        )


class SimulationDeadlockError(SimulationError):
    """Raised when simulation reaches a deadlock state"""

    def __init__(self, blocked_tasks: int, reason: str):
        self.blocked_tasks = blocked_tasks
        self.reason = reason
        super().__init__(
            f"Simulation deadlock detected: {blocked_tasks} tasks blocked - {reason}"
        )


# ===============================================================================
# EVENT SYSTEM EXCEPTIONS
# ===============================================================================

class EventError(FactorySimulationError):
    """Base exception for event system errors"""
    pass


class EventHandlerError(EventError):
    """Raised when an event handler fails"""

    def __init__(self, event_type: str, handler_name: str, reason: str):
        self.event_type = event_type
        self.handler_name = handler_name
        self.reason = reason
        super().__init__(
            f"Event handler '{handler_name}' failed for event '{event_type}': {reason}"
        )


class EventQueueOverflowError(EventError):
    """Raised when event queue exceeds capacity"""

    def __init__(self, queue_size: int, max_size: int):
        self.queue_size = queue_size
        self.max_size = max_size
        super().__init__(
            f"Event queue overflow: {queue_size} events, max {max_size}"
        )


# ===============================================================================
# UTILITY FUNCTIONS
# ===============================================================================

def format_validation_errors(errors: List[str], prefix: str = "  - ") -> str:
    """
    Format a list of validation errors for display

    Args:
        errors: List of error messages
        prefix: Prefix for each error line

    Returns:
        Formatted error string
    """
    if not errors:
        return "No errors"
    return "\n".join(f"{prefix}{err}" for err in errors)


def create_context_message(context: Optional[str], message: str) -> str:
    """
    Create a contextualized error message

    Args:
        context: Optional context information
        message: Base error message

    Returns:
        Contextualized message
    """
    if context:
        return f"{message} (context: {context})"
    return message