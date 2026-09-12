#!/usr/bin/env python3
"""
Factory Builder - Creates fully configured factories from spec files

This module bridges the spec system with the modular architecture, allowing
complete factory definition (both WHAT and HOW) through configuration files.
"""

from typing import Optional, Dict, List
import argparse
import logging
import sys

from .spec_loader import SpecLoader
from .modular_factory_adapter import ModularFactory, ModularFactoryBridge
from .modular_framework import SubsystemRegistry, UpdateStrategy, SubsystemConfig, ConfigManager
from .exceptions import (
    SubsystemNotFoundError,
    SubsystemConfigError
)

# Import custom subsystems so they register with SubsystemRegistry
from . import custom_subsystems  # noqa: F401

# Configure module logger
logger = logging.getLogger(__name__)


def create_factory_from_spec(
    spec_path: str,
    profile: Optional[str] = None,
    update_strategy: UpdateStrategy = UpdateStrategy.SEQUENTIAL
) -> ModularFactory:
    """
    Create a hybrid ModularFactory wired to the classic Factory replication engine.

    Loads the spec, builds a ModularFactoryBridge hybrid (real Factory + modular
    plugins), and returns a ModularFactory whose run_simulation drives replication.

    Args:
        spec_path: Path to the spec file (.json, .yaml, .spec)
        profile: Optional profile name to apply from spec.profiles
        update_strategy: How modular plugins should be updated (default: SEQUENTIAL)

    Returns:
        ModularFactory configured for hybrid replication (not an empty sandbox loop)

    Raises:
        SpecNotFoundError: If spec file doesn't exist
        SpecParseError: If spec file cannot be parsed
        SpecValidationError: If spec validation fails
        SubsystemNotFoundError: If subsystem implementation not found
        SubsystemConfigError: If subsystem configuration is invalid
    """
    loader = SpecLoader()
    spec = loader.load_spec(spec_path)

    # Validate custom implementations before wiring
    if spec.subsystem_implementations:
        available = SubsystemRegistry.list_available()
        for role, impl_name in spec.subsystem_implementations.items():
            if impl_name not in available:
                raise SubsystemConfigError(
                    role,
                    str(SubsystemNotFoundError(impl_name, available)),
                )

    config = loader.create_config(spec, profile)
    resource_enum = loader.create_resource_enum(spec)
    recipes = loader.create_recipes(spec, resource_enum)
    module_specs = loader.create_module_specs(spec)

    spec_dict = {
        "subsystem_data": spec.subsystem_data,
        "resources": spec.resources,
        "target_modules": spec.target_modules,
    }

    logger.info(
        "Creating hybrid Factory from spec: %s",
        spec.metadata.get("name", "Unknown"),
    )

    bridge = ModularFactoryBridge(
        config=config,
        spec_dict=spec_dict,
        resource_enum=resource_enum,
        recipes=recipes,
        module_specs=module_specs,
        subsystem_implementations=spec.subsystem_implementations or {},
        subsystem_data=spec.subsystem_data or {},
    )
    hybrid_factory = bridge.create_hybrid_factory()

    config_manager = ConfigManager(base_config=config)
    factory = ModularFactory(
        orchestrator=bridge.modular_factory.orchestrator,
        config_manager=config_manager,
        hybrid_factory=hybrid_factory,
    )
    factory.set_update_strategy(update_strategy)
    if update_strategy != UpdateStrategy.SEQUENTIAL:
        logger.info("Update strategy: %s", update_strategy.name)

    factory.spec = spec  # type: ignore
    factory.resource_enum = resource_enum  # type: ignore
    factory.bridge = bridge  # type: ignore

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
    all_valid: bool = True

    if spec.subsystem_implementations:
        logger.info("Validating subsystem implementations:")

        for role, impl_name in spec.subsystem_implementations.items():
            if impl_name in available:
                logger.info(f"  ✓ {role}: {impl_name}")
            else:
                logger.error(f"  ✗ {role}: {impl_name} NOT FOUND")
                logger.error(f"     Available: {', '.join(sorted(available))}")
                all_valid = False
    else:
        logger.info("No subsystem implementations defined in spec")

    return all_valid


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for factory-builder."""
    parser = argparse.ArgumentParser(
        prog="factory-builder",
        description="Create and validate modular factories from spec files",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List available subsystem implementations")

    validate_p = sub.add_parser("validate", help="Validate subsystems in a spec")
    validate_p.add_argument("spec", help="Path to spec file")

    create_p = sub.add_parser("create", help="Create hybrid factory from spec")
    create_p.add_argument("spec", help="Path to spec file")
    create_p.add_argument("profile", nargs="?", default=None, help="Optional profile")

    args = parser.parse_args(argv)

    print("=== Factory Builder ===\n")

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "list":
        subsystems = list_available_subsystems()
        print("Available subsystem implementations:\n")
        for name, desc in sorted(subsystems.items()):
            print(f"  {name:25} - {desc}")
        return 0

    if args.command == "validate":
        if validate_spec_subsystems(args.spec):
            print("\n✓ All subsystems valid")
            return 0
        print("\n✗ Invalid subsystems found")
        return 1

    if args.command == "create":
        factory = create_factory_from_spec(args.spec, args.profile)
        print("\n✓ Hybrid factory created successfully")
        print(f"  Plugins: {len(factory.orchestrator.subsystems)}")
        print(f"  Engine: classic Factory (hybrid)")
        print("  Ready to run simulation")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())