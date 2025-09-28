#!/usr/bin/env python3
"""
Dynamic Subsystems for Self-Replicating Factory

This module provides dynamic versions of factory subsystems that can work
with any ResourceType enum loaded from spec files, eliminating hardcoded
resource references.
"""

from typing import Dict, Any, Optional, Tuple, List
from enum import Enum
from collections import defaultdict
from dataclasses import dataclass, field
import logging

# Set up logging
logger = logging.getLogger(__name__)


# ===============================================================================
# BASE DYNAMIC SUBSYSTEM
# ===============================================================================

class DynamicSubsystemBase:
    """Base class for dynamic subsystems"""

    def __init__(self, config: Dict[str, Any], resource_enum: Optional[Enum] = None):
        """
        Initialize dynamic subsystem

        Args:
            config: Configuration dictionary from spec
            resource_enum: ResourceType enum (can be dynamically generated)
        """
        self.config = config or {}
        self.resource_enum = resource_enum
        self._resource_cache = {}  # Cache for enum lookups
        self.enabled = self.config.get('enabled', True)

    def _get_resource_enum(self, resource_name: str) -> Optional[Any]:
        """
        Get enum value from string name with caching

        Args:
            resource_name: String name of resource

        Returns:
            Enum value or None if not found
        """
        if not self.resource_enum:
            return None

        # Check cache first
        if resource_name in self._resource_cache:
            return self._resource_cache[resource_name]

        # Try to get from enum
        try:
            if hasattr(self.resource_enum, resource_name):
                enum_val = getattr(self.resource_enum, resource_name)
                self._resource_cache[resource_name] = enum_val
                return enum_val
        except Exception as e:
            logger.warning(f"Could not get enum for {resource_name}: {e}")

        return None

    def _convert_config_to_enum_dict(self, config_dict: Dict[str, Any]) -> Dict:
        """
        Convert a config dictionary with string keys to enum keys

        Args:
            config_dict: Dictionary with string resource names as keys

        Returns:
            Dictionary with enum values as keys
        """
        result = {}
        for resource_name, value in config_dict.items():
            enum_val = self._get_resource_enum(resource_name)
            if enum_val:
                result[enum_val] = value
            else:
                logger.debug(f"Resource {resource_name} not found in enum")
        return result


# ===============================================================================
# DYNAMIC WASTE STREAM
# ===============================================================================

class DynamicWasteStream:
    """Dynamic waste stream that works with any ResourceType enum"""

    def __init__(self, config: Optional[Dict] = None, resource_enum: Optional[Enum] = None):
        """
        Initialize dynamic waste stream

        Args:
            config: Configuration with recyclable_materials
            resource_enum: ResourceType enum
        """
        self.config = config or {}
        self.resource_enum = resource_enum
        self.waste_inventory = defaultdict(float)
        self._resource_cache = {}

        # Process recyclable materials from config
        self.recyclable_materials = {}
        if 'recyclable_materials' in self.config:
            self._load_recyclable_materials()
        else:
            # Default fallback values
            self._load_default_recyclables()

    def _get_resource_enum(self, resource_name: str) -> Optional[Any]:
        """Get enum value from string name with caching"""
        if not self.resource_enum:
            return None

        if resource_name in self._resource_cache:
            return self._resource_cache[resource_name]

        try:
            if hasattr(self.resource_enum, resource_name):
                enum_val = getattr(self.resource_enum, resource_name)
                self._resource_cache[resource_name] = enum_val
                return enum_val
        except Exception:
            pass

        return None

    def _load_recyclable_materials(self):
        """Load recyclable materials from config"""
        for resource_name, recovery_rate in self.config['recyclable_materials'].items():
            enum_val = self._get_resource_enum(resource_name)
            if enum_val:
                self.recyclable_materials[enum_val] = recovery_rate

    def _load_default_recyclables(self):
        """Load default recyclable materials if available in enum"""
        defaults = {
            'STEEL': 0.95,
            'ALUMINUM_SHEET': 0.90,
            'COPPER_WIRE': 0.85,
            'PLASTIC': 0.60,
            'GLASS': 0.80,
            'SILICON_WAFER': 0.70,
        }
        for resource_name, recovery_rate in defaults.items():
            enum_val = self._get_resource_enum(resource_name)
            if enum_val:
                self.recyclable_materials[enum_val] = recovery_rate

    def add_waste(self, waste_type, quantity: float):
        """Add waste to stream"""
        self.waste_inventory[waste_type] += quantity

    def process_recycling(self, waste_type, quantity: float) -> float:
        """Process waste for recycling"""
        if waste_type not in self.recyclable_materials:
            return 0.0
        available = min(quantity, self.waste_inventory.get(waste_type, 0))
        recovery_rate = self.recyclable_materials[waste_type]
        recovered = available * recovery_rate
        self.waste_inventory[waste_type] -= available
        return recovered

    def get_total_waste(self) -> float:
        """Get total waste in system"""
        return sum(self.waste_inventory.values())


# ===============================================================================
# DYNAMIC SOFTWARE PRODUCTION SYSTEM
# ===============================================================================

class DynamicSoftwareProductionSystem:
    """Dynamic software production system that works with any ResourceType enum"""

    def __init__(self, config: Optional[Dict] = None, resource_enum: Optional[Enum] = None):
        """
        Initialize dynamic software production system

        Args:
            config: Configuration with bug_rates
            resource_enum: ResourceType enum
        """
        self.config = config or {}
        self.resource_enum = resource_enum
        self.software_library = {}
        self.development_hours = defaultdict(float)
        self.version_counter = defaultdict(int)
        self._resource_cache = {}

        # Process bug rates from config
        self.bug_rates = {}
        if 'bug_rates' in self.config:
            self._load_bug_rates()
        else:
            self._load_default_bug_rates()

    def _get_resource_enum(self, resource_name: str) -> Optional[Any]:
        """Get enum value from string name with caching"""
        if not self.resource_enum:
            return None

        if resource_name in self._resource_cache:
            return self._resource_cache[resource_name]

        try:
            if hasattr(self.resource_enum, resource_name):
                enum_val = getattr(self.resource_enum, resource_name)
                self._resource_cache[resource_name] = enum_val
                return enum_val
        except Exception:
            pass

        return None

    def _load_bug_rates(self):
        """Load bug rates from config"""
        for software_name, bug_rate in self.config['bug_rates'].items():
            enum_val = self._get_resource_enum(software_name)
            if enum_val:
                self.bug_rates[enum_val] = bug_rate

    def _load_default_bug_rates(self):
        """Load default bug rates if available in enum"""
        defaults = {
            'PLC_PROGRAM': 0.05,
            'ROBOT_FIRMWARE': 0.08,
            'AI_MODEL': 0.15,
            'SCADA_SYSTEM': 0.10
        }
        for software_name, bug_rate in defaults.items():
            enum_val = self._get_resource_enum(software_name)
            if enum_val:
                self.bug_rates[enum_val] = bug_rate

    def develop_software(self, software_type, dev_hours: float) -> Dict:
        """Develop software with quality metrics"""
        self.development_hours[software_type] += dev_hours

        # Version management
        self.version_counter[software_type] += 1
        version = f"v{self.version_counter[software_type]}.0"

        # Calculate bugs based on complexity
        base_bug_rate = self.bug_rates.get(software_type, 0.1)

        # Experience reduces bugs
        experience_factor = max(0.5, 1.0 - self.development_hours[software_type] / 1000)
        actual_bug_rate = base_bug_rate * experience_factor

        # Testing reduces bugs by 90%
        bugs_after_testing = actual_bug_rate * 0.1

        # Store in library
        self.software_library[software_type] = {
            "version": version,
            "dev_hours": self.development_hours[software_type],
            "bug_rate": bugs_after_testing,
            "ready": True
        }

        return self.software_library[software_type]


# ===============================================================================
# DYNAMIC STORAGE SYSTEM
# ===============================================================================

@dataclass
class DynamicStorageSystem:
    """Dynamic storage system that works with any ResourceType enum"""

    total_volume_m3: float
    total_weight_capacity_tons: float
    current_inventory: Dict[Any, float] = field(default_factory=dict)
    waste_inventory: Dict[Any, float] = field(default_factory=dict)
    enabled: bool = True
    temperature_controlled: bool = True
    contamination_controlled: bool = True

    def __init__(self,
                 total_volume_m3: float,
                 total_weight_capacity_tons: float,
                 config: Optional[Dict] = None,
                 resource_enum: Optional[Enum] = None,
                 enabled: bool = True):
        """
        Initialize dynamic storage system

        Args:
            total_volume_m3: Total storage volume
            total_weight_capacity_tons: Total weight capacity
            config: Configuration with material_properties
            resource_enum: ResourceType enum
            enabled: Whether storage limits are enabled
        """
        self.total_volume_m3 = total_volume_m3
        self.total_weight_capacity_tons = total_weight_capacity_tons
        self.current_inventory = defaultdict(float)
        self.waste_inventory = defaultdict(float)
        self.enabled = enabled
        self.config = config or {}
        self.resource_enum = resource_enum
        self._resource_cache = {}

        # Material properties from config or spec
        self.material_properties = {}
        if 'material_properties' in self.config:
            self._load_material_properties()
        else:
            self._load_default_properties()

    def _get_resource_enum(self, resource_name: str) -> Optional[Any]:
        """Get enum value from string name with caching"""
        if not self.resource_enum:
            return None

        if resource_name in self._resource_cache:
            return self._resource_cache[resource_name]

        try:
            if hasattr(self.resource_enum, resource_name):
                enum_val = getattr(self.resource_enum, resource_name)
                self._resource_cache[resource_name] = enum_val
                return enum_val
        except Exception:
            pass

        return None

    def _load_material_properties(self):
        """Load material properties from config"""
        for resource_name, props in self.config['material_properties'].items():
            enum_val = self._get_resource_enum(resource_name)
            if enum_val:
                if isinstance(props, dict):
                    # Dictionary format
                    density = props.get('density', 1.0)
                    temp = props.get('storage_temp', 25)
                    contamination = props.get('contamination_sensitivity', 0.5)
                else:
                    # Tuple format (density, temp, contamination)
                    density = props[0] if len(props) > 0 else 1.0
                    temp = props[1] if len(props) > 1 else 25
                    contamination = props[2] if len(props) > 2 else 0.5

                self.material_properties[enum_val] = (density, temp, contamination)

    def _load_default_properties(self):
        """Load default material properties if available in enum"""
        defaults = {
            'SILICON_ORE': (2.3, 25, 0.1),
            'IRON_ORE': (4.0, 25, 0.1),
            'SILICON_WAFER': (2.3, 22, 1.0),
            'INTEGRATED_CIRCUIT': (0.2, 22, 1.0),
            'CHEMICAL_PUMP': (5.0, 25, 0.3),
            'LITHIUM_COMPOUND': (1.5, 20, 0.8),
            'SULFURIC_ACID': (1.8, 15, 0.5),
            'ORGANIC_SOLVENT': (0.8, 10, 0.6),
        }
        for resource_name, props in defaults.items():
            enum_val = self._get_resource_enum(resource_name)
            if enum_val:
                self.material_properties[enum_val] = props

    def get_material_properties(self, resource) -> Tuple[float, float, float]:
        """Get material properties with defaults"""
        # Try from configured properties first
        if resource in self.material_properties:
            return self.material_properties[resource]

        # Try from spec data if we have access to spec
        if hasattr(resource, 'value') and self.config.get('spec_resources'):
            resource_name = resource.value.upper()
            if resource_name in self.config['spec_resources']:
                spec_props = self.config['spec_resources'][resource_name]
                # spec_props is a ResourceSpec dataclass, not a dict
                density = getattr(spec_props, 'density', 1.0)
                temp = getattr(spec_props, 'storage_temp', 25)
                contamination = getattr(spec_props, 'contamination_sensitivity', 0.5)
                return (density, temp, contamination)

        # Default fallback
        return (1.0, 25, 0.5)

    def can_store(self, resource, quantity: float) -> Tuple[bool, str]:
        """Check if storage is available with reason"""
        if not self.enabled:
            return (True, "OK")

        # Get material properties
        density, storage_temp, contamination = self.get_material_properties(resource)

        # Calculate volume needed
        volume_needed = quantity / density if density > 0 else quantity

        # Check volume constraint
        current_volume = sum(
            qty / self.get_material_properties(res)[0]
            for res, qty in self.current_inventory.items()
        )

        if current_volume + volume_needed > self.total_volume_m3:
            return (False, f"Insufficient volume: need {volume_needed:.1f}m³")

        # Check weight constraint
        current_weight = sum(self.current_inventory.values())
        if current_weight + quantity > self.total_weight_capacity_tons:
            return (False, f"Insufficient weight capacity: need {quantity:.1f}t")

        return (True, "OK")

    def add_resource(self, resource, quantity: float) -> bool:
        """Add resource to storage"""
        can_store, reason = self.can_store(resource, quantity)
        if not can_store:
            logger.warning(f"Cannot store {quantity} of {resource}: {reason}")
            return False

        if resource not in self.current_inventory:
            self.current_inventory[resource] = 0
        self.current_inventory[resource] += quantity
        return True

    def get_available(self, resource) -> float:
        """Get available quantity of resource"""
        return self.current_inventory.get(resource, 0.0)

    def get_storage_utilization(self) -> Dict[str, float]:
        """Get storage utilization metrics"""
        # Volume utilization
        current_volume = sum(
            qty / self.get_material_properties(res)[0]
            for res, qty in self.current_inventory.items()
        )
        volume_util = current_volume / self.total_volume_m3 if self.total_volume_m3 > 0 else 0

        # Weight utilization
        current_weight = sum(self.current_inventory.values())
        weight_util = current_weight / self.total_weight_capacity_tons if self.total_weight_capacity_tons > 0 else 0

        return {
            "volume_utilization": volume_util,
            "weight_utilization": weight_util,
            "current_volume_m3": current_volume,
            "current_weight_tons": current_weight
        }


# ===============================================================================
# SUBSYSTEM FACTORY
# ===============================================================================

class SubsystemFactory:
    """Factory for creating dynamic subsystems with proper configuration"""

    def __init__(self, spec: Optional[Dict] = None, resource_enum: Optional[Enum] = None):
        """
        Initialize subsystem factory

        Args:
            spec: Factory spec dictionary
            resource_enum: ResourceType enum
        """
        self.spec = spec or {}
        self.resource_enum = resource_enum
        self.subsystem_data = self.spec.get('subsystem_data', {})

    def create_waste_stream(self, config: Optional[Dict] = None) -> DynamicWasteStream:
        """Create dynamic waste stream"""
        # Merge spec config with provided config
        waste_config = self.subsystem_data.get('waste_stream', {})
        if config:
            waste_config.update(config)

        return DynamicWasteStream(
            config=waste_config,
            resource_enum=self.resource_enum
        )

    def create_software_system(self, config: Optional[Dict] = None) -> DynamicSoftwareProductionSystem:
        """Create dynamic software production system"""
        # Merge spec config with provided config
        software_config = self.subsystem_data.get('software_production', {})
        if config:
            software_config.update(config)

        return DynamicSoftwareProductionSystem(
            config=software_config,
            resource_enum=self.resource_enum
        )

    def create_storage_system(self,
                              total_volume_m3: float,
                              total_weight_capacity_tons: float,
                              config: Optional[Dict] = None,
                              enabled: bool = True) -> DynamicStorageSystem:
        """Create dynamic storage system"""
        # Merge spec config with provided config
        storage_config = self.subsystem_data.get('storage', {})
        if config:
            storage_config.update(config)

        # Add spec resources to config if available
        if 'resources' in self.spec:
            storage_config['spec_resources'] = self.spec['resources']

        return DynamicStorageSystem(
            total_volume_m3=total_volume_m3,
            total_weight_capacity_tons=total_weight_capacity_tons,
            config=storage_config,
            resource_enum=self.resource_enum,
            enabled=enabled
        )

    def create_all_subsystems(self, factory_config: Dict) -> Dict:
        """Create all dynamic subsystems"""
        subsystems = {}

        # Create waste stream
        subsystems['waste_stream'] = self.create_waste_stream()

        # Create software system
        subsystems['software_system'] = self.create_software_system()

        # Create storage system
        subsystems['storage_system'] = self.create_storage_system(
            total_volume_m3=factory_config.get('max_storage_volume_m3', 15000),
            total_weight_capacity_tons=factory_config.get('max_storage_weight_tons', 10000),
            enabled=factory_config.get('enable_storage_limits', True)
        )

        return subsystems


# ===============================================================================
# COMPATIBILITY LAYER
# ===============================================================================

def create_compatible_subsystems(resource_enum: Optional[Enum] = None,
                                 spec: Optional[Dict] = None,
                                 config: Optional[Dict] = None) -> Dict:
    """
    Create subsystems that are compatible with the existing factory

    Args:
        resource_enum: ResourceType enum (can be dynamic or default)
        spec: Spec dictionary
        config: Factory configuration

    Returns:
        Dictionary of subsystems ready to use
    """
    factory = SubsystemFactory(spec=spec, resource_enum=resource_enum)
    return factory.create_all_subsystems(config or {})