#!/usr/bin/env python3
"""
Configuration validation using Pydantic

This module provides validated configuration schemas for the factory simulation,
ensuring that all configuration parameters are valid at runtime.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# ===============================================================================
# ENUMS
# ===============================================================================

class UpdateStrategyConfig(str, Enum):
    """Update strategy options"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY = "priority"
    DEPENDENCY = "dependency"


# ===============================================================================
# BASE CONFIGURATION
# ===============================================================================

class EnergyConfig(BaseModel):
    """Energy system configuration"""

    initial_solar_capacity_kw: float = Field(
        default=100,
        gt=0,
        le=100000,
        description="Initial solar panel capacity in kilowatts"
    )

    solar_panel_efficiency: float = Field(
        default=0.22,
        gt=0,
        le=1.0,
        description="Solar panel conversion efficiency (0-1)"
    )

    battery_efficiency: float = Field(
        default=0.95,
        gt=0,
        le=1.0,
        description="Battery charge/discharge efficiency"
    )

    battery_capacity_kwh: float = Field(
        default=500,
        gt=0,
        description="Battery storage capacity in kWh"
    )

    latitude: float = Field(
        default=35.0,
        ge=-90,
        le=90,
        description="Factory latitude for solar calculations"
    )

    average_cloud_cover: float = Field(
        default=0.3,
        ge=0,
        le=1.0,
        description="Average cloud cover factor (0-1)"
    )


class ProcessingConfig(BaseModel):
    """Processing and production configuration"""

    mining_power_multiplier: float = Field(
        default=1.0,
        gt=0,
        le=10,
        description="Mining operations power multiplier"
    )

    processing_speed_multiplier: float = Field(
        default=1.0,
        gt=0,
        le=10,
        description="Processing speed multiplier"
    )

    assembly_speed_multiplier: float = Field(
        default=1.0,
        gt=0,
        le=10,
        description="Assembly operations speed multiplier"
    )

    parallel_processing_limit: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Maximum parallel tasks per module"
    )

    maintenance_interval_hours: float = Field(
        default=500,
        gt=0,
        description="Hours between maintenance cycles"
    )

    learning_curve_factor: float = Field(
        default=0.95,
        gt=0,
        le=1.0,
        description="Learning curve improvement factor"
    )

    redundancy_factor: float = Field(
        default=1.2,
        ge=1.0,
        le=10.0,
        description="System redundancy multiplier"
    )


class FeatureToggles(BaseModel):
    """Feature toggle configuration"""

    enable_capacity_limits: bool = Field(
        default=True,
        description="Enable module throughput capacity limits"
    )

    enable_degradation: bool = Field(
        default=True,
        description="Enable equipment degradation over time"
    )

    enable_quality_control: bool = Field(
        default=True,
        description="Enable quality control and defect rates"
    )

    enable_weather: bool = Field(
        default=True,
        description="Enable realistic weather effects on solar"
    )

    enable_maintenance: bool = Field(
        default=True,
        description="Enable required maintenance downtime"
    )

    enable_storage_limits: bool = Field(
        default=True,
        description="Enable physical storage constraints"
    )

    enable_batch_processing: bool = Field(
        default=True,
        description="Enable batch size requirements"
    )

    enable_transport_time: bool = Field(
        default=True,
        description="Enable realistic transport delays"
    )

    enable_contamination: bool = Field(
        default=True,
        description="Enable contamination tracking"
    )

    enable_thermal_management: bool = Field(
        default=True,
        description="Enable thermal constraints"
    )

    enable_software_production: bool = Field(
        default=True,
        description="Enable software development simulation"
    )

    enable_waste_recycling: bool = Field(
        default=True,
        description="Enable waste recycling systems"
    )


class PhysicalConstraints(BaseModel):
    """Physical facility constraints"""

    factory_area_m2: float = Field(
        default=20000,
        gt=0,
        description="Total factory floor area in square meters"
    )

    max_storage_volume_m3: float = Field(
        default=15000,
        gt=0,
        description="Maximum storage volume in cubic meters"
    )

    max_storage_weight_tons: float = Field(
        default=10000,
        gt=0,
        description="Maximum storage weight in tons"
    )

    ambient_temperature: float = Field(
        default=25,
        ge=-50,
        le=60,
        description="Ambient temperature in Celsius"
    )


class QualityConfig(BaseModel):
    """Quality control configuration"""

    target_quality_rate: float = Field(
        default=0.95,
        gt=0,
        le=1.0,
        description="Target quality pass rate"
    )

    cleanroom_class: int = Field(
        default=1000,
        ge=1,
        le=100000,
        description="Cleanroom classification (particles per cubic meter)"
    )


class TransportConfig(BaseModel):
    """Transport system configuration"""

    agv_fleet_size: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Number of AGVs in fleet"
    )

    conveyor_length_m: float = Field(
        default=500,
        gt=0,
        description="Total conveyor belt length in meters"
    )


# ===============================================================================
# MAIN FACTORY CONFIGURATION
# ===============================================================================

class FactoryConfig(BaseModel):
    """Complete validated factory configuration"""

    # Sub-configurations
    energy: EnergyConfig = Field(default_factory=EnergyConfig)
    processing: ProcessingConfig = Field(default_factory=ProcessingConfig)
    features: FeatureToggles = Field(default_factory=FeatureToggles)
    physical: PhysicalConstraints = Field(default_factory=PhysicalConstraints)
    quality: QualityConfig = Field(default_factory=QualityConfig)
    transport: TransportConfig = Field(default_factory=TransportConfig)

    # Additional parameters
    simulation_name: Optional[str] = Field(
        default=None,
        description="Name for this simulation run"
    )

    output_file: str = Field(
        default="factory_simulation_log.json",
        description="Output file path for simulation results"
    )

    max_simulation_hours: float = Field(
        default=10000,
        gt=0,
        le=100000,
        description="Maximum simulation time in hours"
    )

    time_step_hours: float = Field(
        default=0.1,
        gt=0,
        le=1.0,
        description="Simulation time step in hours"
    )

    @model_validator(mode='after')
    def validate_config_consistency(self):
        """Validate that configuration is internally consistent"""
        # Battery capacity should be reasonable relative to solar capacity
        if self.energy.battery_capacity_kwh > self.energy.initial_solar_capacity_kw * 24:
            raise ValueError(
                f"Battery capacity ({self.energy.battery_capacity_kwh} kWh) is unreasonably "
                f"large relative to solar capacity ({self.energy.initial_solar_capacity_kw} kW)"
            )

        # Storage constraints should be reasonable
        if self.physical.max_storage_weight_tons > self.physical.max_storage_volume_m3:
            # This would mean average density > 1 ton/m³, which is reasonable for factory materials
            pass

        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert to flat dictionary for legacy compatibility"""
        result = {}

        # Flatten energy config
        for key, value in self.energy.model_dump().items():
            result[key] = value

        # Flatten processing config
        for key, value in self.processing.model_dump().items():
            result[key] = value

        # Flatten feature toggles
        for key, value in self.features.model_dump().items():
            result[key] = value

        # Flatten physical constraints
        for key, value in self.physical.model_dump().items():
            result[key] = value

        # Flatten quality config
        for key, value in self.quality.model_dump().items():
            result[key] = value

        # Flatten transport config
        for key, value in self.transport.model_dump().items():
            result[key] = value

        # Add top-level params
        result["simulation_name"] = self.simulation_name
        result["output_file"] = self.output_file
        result["max_simulation_hours"] = self.max_simulation_hours
        result["time_step_hours"] = self.time_step_hours

        return result

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "FactoryConfig":
        """Create from flat dictionary (legacy format)"""
        # Group by category
        energy_params = {}
        processing_params = {}
        feature_params = {}
        physical_params = {}
        quality_params = {}
        transport_params = {}
        top_level_params = {}

        # Map known keys to categories
        energy_keys = set(EnergyConfig.model_fields.keys())
        processing_keys = set(ProcessingConfig.model_fields.keys())
        feature_keys = set(FeatureToggles.model_fields.keys())
        physical_keys = set(PhysicalConstraints.model_fields.keys())
        quality_keys = set(QualityConfig.model_fields.keys())
        transport_keys = set(TransportConfig.model_fields.keys())

        for key, value in config_dict.items():
            if key in energy_keys:
                energy_params[key] = value
            elif key in processing_keys:
                processing_params[key] = value
            elif key in feature_keys:
                feature_params[key] = value
            elif key in physical_keys:
                physical_params[key] = value
            elif key in quality_keys:
                quality_params[key] = value
            elif key in transport_keys:
                transport_params[key] = value
            else:
                top_level_params[key] = value

        return cls(
            energy=EnergyConfig(**energy_params) if energy_params else EnergyConfig(),
            processing=ProcessingConfig(**processing_params) if processing_params else ProcessingConfig(),
            features=FeatureToggles(**feature_params) if feature_params else FeatureToggles(),
            physical=PhysicalConstraints(**physical_params) if physical_params else PhysicalConstraints(),
            quality=QualityConfig(**quality_params) if quality_params else QualityConfig(),
            transport=TransportConfig(**transport_params) if transport_params else TransportConfig(),
            **top_level_params
        )


# ===============================================================================
# UTILITY FUNCTIONS
# ===============================================================================

def validate_config(config_dict: Dict[str, Any]) -> FactoryConfig:
    """
    Validate a configuration dictionary.

    Args:
        config_dict: Dictionary with configuration parameters

    Returns:
        Validated FactoryConfig instance

    Raises:
        ValidationError: If configuration is invalid

    Example:
        >>> config = {"initial_solar_capacity_kw": 150, "latitude": 40.0}
        >>> validated = validate_config(config)
        >>> print(validated.energy.initial_solar_capacity_kw)
        150.0
    """
    return FactoryConfig.from_dict(config_dict)


def get_default_config() -> FactoryConfig:
    """
    Get default factory configuration.

    Returns:
        FactoryConfig with default values
    """
    return FactoryConfig()


if __name__ == "__main__":
    # Demonstration
    print("Factory Configuration Validation")
    print("=" * 60)

    # Create default config
    config = get_default_config()
    print("\nDefault Configuration:")
    print(f"  Solar Capacity: {config.energy.initial_solar_capacity_kw} kW")
    print(f"  Parallel Processing Limit: {config.processing.parallel_processing_limit}")
    print(f"  Storage Volume: {config.physical.max_storage_volume_m3} m³")

    # Validate custom config
    custom_config = {
        "initial_solar_capacity_kw": 200,
        "latitude": 45.0,
        "parallel_processing_limit": 20,
        "enable_degradation": False
    }

    validated = validate_config(custom_config)
    print("\nValidated Custom Configuration:")
    print(f"  Solar Capacity: {validated.energy.initial_solar_capacity_kw} kW")
    print(f"  Latitude: {validated.energy.latitude}°")
    print(f"  Degradation Enabled: {validated.features.enable_degradation}")

    # Convert back to dict
    config_dict = validated.to_dict()
    print(f"\nExported {len(config_dict)} configuration parameters")

    print("\n✅ Configuration validation working correctly!")