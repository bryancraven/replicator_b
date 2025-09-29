#!/usr/bin/env python3
"""
Factory Builder - Creates fully configured factories from spec files

This module bridges the spec system with the modular architecture, allowing
complete factory definition (both WHAT and HOW) through configuration files.
"""

from typing import Optional, Any, Dict, List
from spec_loader import SpecLoader, FactorySpec
from modular_factory_adapter import ModularFactory
from modular_framework import SubsystemRegistry, UpdateStrategy, SubsystemConfig
from exceptions import (
    SubsystemNotFoundError,
    SubsystemConfigError,
    SpecNotFoundError
)

# Import custom subsystems to register them
import custom_subsystems


def create_factory_from_spec(
    spec_path: str,
    profile: Optional[str] = None,
    update_strategy: UpdateStrategy = UpdateStrategy.SEQUENTIAL
) -> ModularFactory:
    """
    Create a fully configured ModularFactory from a spec file.

    This function:
    1. Loads the spec file
    2. Creates a ModularFactory with the spec's configuration
    3. Adds subsystems based on subsystem_implementations section
    4. Configures each subsystem with subsystem_data
    5. Sets the update strategy

    Args:
        spec_path: Path to the spec file (.json, .yaml, .spec)
        profile: Optional profile name to apply from spec.profiles
        update_strategy: How subsystems should be updated (default: SEQUENTIAL)

    Returns:
        Fully configured ModularFactory ready to run simulation

    Raises:
        SpecNotFoundError: If spec file doesn't exist
        SpecParseError: If spec file cannot be parsed
        SpecValidationError: If spec validation fails
        SubsystemNotFoundError: If subsystem implementation not found
        SubsystemConfigError: If subsystem configuration is invalid

    Example:
        >>> factory = create_factory_from_spec("specs/genetic_optimized.json")
        >>> result = factory.run_simulation(max_hours=1000)
        >>> print(f"Completed in {result['simulation_time']:.1f} hours")
    """
    # Load the spec
    loader = SpecLoader()
    spec = loader.load_spec(spec_path)

    # Create configuration
    config = loader.create_config(spec, profile)

    # Create resource enum
    resource_enum = loader.create_resource_enum(spec)

    # Create the modular factory
    print(f"Creating ModularFactory from spec: {spec.metadata.get('name', 'Unknown')}")
    # ModularFactory expects orchestrator and config_manager, not config dict
    from modular_framework import ConfigManager
    config_manager = ConfigManager(base_config=config)
    factory = ModularFactory(config_manager=config_manager)

    # Add spec-defined subsystem implementations
    if spec.subsystem_implementations:
        print(f"Configuring {len(spec.subsystem_implementations)} custom subsystems:")

        # Clear default subsystems first if we're replacing them with spec-defined ones
        factory.orchestrator.subsystems.clear()

        for role, impl_name in spec.subsystem_implementations.items():
            try:
                # Check if implementation exists
                if impl_name not in SubsystemRegistry.list_available():
                    raise SubsystemNotFoundError(impl_name, SubsystemRegistry.list_available())

                # Create subsystem from registry
                subsystem = SubsystemRegistry.create(impl_name)

                # Get configuration for this subsystem if available
                subsystem_config = None
                if spec.subsystem_data and role in spec.subsystem_data:
                    subsystem_config = SubsystemConfig(spec.subsystem_data[role])

                # Add to factory
                factory.add_custom_subsystem(role, subsystem, subsystem_config)
                print(f"  ✓ {role}: {impl_name}")

            except (ValueError, SubsystemNotFoundError) as e:
                raise SubsystemConfigError(role, str(e)) from e

    # Set update strategy
    factory.set_update_strategy(update_strategy)
    if update_strategy != UpdateStrategy.SEQUENTIAL:
        print(f"Update strategy: {update_strategy.name}")

    # Store spec data for subsystems that might need it
    factory.spec = spec
    factory.resource_enum = resource_enum

    return factory


def list_available_subsystems() -> Dict[str, str]:
    """
    List all available subsystem implementations that can be used in specs.

    Returns:
        Dictionary mapping implementation names to descriptions
    """
    available = SubsystemRegistry.list_available()

    # Add descriptions for known subsystems
    descriptions = {
        # Wrappers for default subsystems
        "transport_wrapper": "Default transport system",
        "waste_wrapper": "Default waste management",
        "thermal_wrapper": "Default thermal management",
        "software_wrapper": "Default software production",
        "cleanroom_wrapper": "Default cleanroom control",
        "storage_wrapper": "Default storage system",
        "energy_wrapper": "Default energy system",

        # Advanced custom subsystems
        "genetic_routing": "Genetic algorithm transport routing",
        "swarm_transport": "Swarm intelligence transport coordination",
        "spc_quality": "Statistical process control for quality",
        "predictive_maintenance": "ML-based predictive maintenance",
        "smart_grid": "Smart grid with demand response",
        "renewable_optimizer": "Multi-source renewable optimization",
        "digital_twin": "Digital twin predictive simulation",

        # Test/mock subsystems
        "adaptive_transport": "Adaptive transport with learning",
        "ml_quality": "Machine learning quality control",
        "mock": "Mock subsystem for testing"
    }

    result = {}
    for name in available:
        result[name] = descriptions.get(name, "Custom subsystem")

    return result


def validate_spec_subsystems(spec_path: str) -> bool:
    """
    Validate that all subsystem implementations in a spec are available.

    Args:
        spec_path: Path to the spec file to validate

    Returns:
        True if all subsystems are valid, False otherwise
    """
    loader = SpecLoader()
    spec = loader.load_spec(spec_path)

    available = SubsystemRegistry.list_available()
    all_valid = True

    if spec.subsystem_implementations:
        print("Validating subsystem implementations:")

        for role, impl_name in spec.subsystem_implementations.items():
            if impl_name in available:
                print(f"  ✓ {role}: {impl_name}")
            else:
                print(f"  ✗ {role}: {impl_name} NOT FOUND")
                print(f"     Available: {', '.join(sorted(available))}")
                all_valid = False
    else:
        print("No subsystem implementations defined in spec")

    return all_valid


if __name__ == "__main__":
    import sys

    print("=== Factory Builder ===\n")

    if len(sys.argv) < 2:
        print("Usage: python factory_builder.py <command> [args]")
        print("\nCommands:")
        print("  list                    - List available subsystems")
        print("  validate <spec>         - Validate subsystems in a spec")
        print("  create <spec> [profile] - Create factory from spec")
        print("\nExamples:")
        print("  python factory_builder.py list")
        print("  python factory_builder.py validate specs/genetic_optimized.json")
        print("  python factory_builder.py create specs/high_reliability.json production")
    else:
        command = sys.argv[1]

        if command == "list":
            subsystems = list_available_subsystems()
            print("Available subsystem implementations:\n")
            for name, desc in sorted(subsystems.items()):
                print(f"  {name:25} - {desc}")

        elif command == "validate" and len(sys.argv) > 2:
            spec_path = sys.argv[2]
            if validate_spec_subsystems(spec_path):
                print("\n✓ All subsystems valid")
            else:
                print("\n✗ Invalid subsystems found")

        elif command == "create" and len(sys.argv) > 2:
            spec_path = sys.argv[2]
            profile = sys.argv[3] if len(sys.argv) > 3 else None

            factory = create_factory_from_spec(spec_path, profile)
            print(f"\n✓ Factory created successfully")
            print(f"  Subsystems: {len(factory.orchestrator.subsystems)}")
            print(f"  Ready to run simulation")

        else:
            print(f"Unknown command or missing arguments: {' '.join(sys.argv[1:])}")