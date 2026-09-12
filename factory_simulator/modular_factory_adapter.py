#!/usr/bin/env python3
"""
Adapter to bridge existing factory simulation with modular framework

This module provides wrappers for existing subsystems to make them compatible
with the new modular architecture, enabling gradual migration.
"""

from typing import Dict, Any, Optional, List
from collections import defaultdict
import json

from .modular_framework import (
    ISubsystem, SubsystemBase, SubsystemConfig, SimulationContext,
    Event, EventType, EventBus, SubsystemOrchestrator, ConfigManager,
    SubsystemRegistry, UpdateStrategy
)

# Import existing subsystems from the main simulation
from .sim import (
    TransportSystem, WasteStream, CleanRoomEnvironment,
    ThermalManagementSystem, SoftwareProductionSystem,
    EnergySystem, Factory, CONFIG, ResourceType
)


# ===============================================================================
# SUBSYSTEM WRAPPERS
# ===============================================================================

class TransportSystemWrapper(SubsystemBase):
    """Wrapper for existing TransportSystem to implement ISubsystem interface"""

    def __init__(self, name: str = "transport"):
        super().__init__(name)
        self.transport_system = None

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        # Create transport system with config
        transport_config = {
            "agv_fleet_size": config.get("agv_fleet_size", 10),
            "conveyor_length_m": config.get("conveyor_length_m", 500),
            "enable_transport_time": config.get("enable_transport_time", True)
        }
        self.transport_system = TransportSystem(transport_config)

        # Subscribe to transport requests
        event_bus.subscribe(EventType.TRANSPORT_REQUESTED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled or not self.transport_system:
            return {}

        # Metrics / event hooks only — Factory drives transport processing
        completed_jobs = []
        self.metrics["active_transports"] = len(
            getattr(self.transport_system, "active_transports", {}) or {}
        )
        self.metrics["completed_jobs"] = len(
            getattr(self.transport_system, "completed_transports", []) or []
        )
        self.metrics["agv_utilization"] = self._calculate_agv_utilization()

        return {
            "completed_transports": len(completed_jobs),
            "active_transports": self.metrics["active_transports"],
        }

    def _calculate_agv_utilization(self) -> float:
        """Calculate AGV fleet utilization"""
        if not self.transport_system.agv_fleet:
            return 0.0
        busy_count = sum(1 for agv in self.transport_system.agv_fleet.values()
                        if agv["status"] != "idle")
        return busy_count / len(self.transport_system.agv_fleet)

    def handle_event(self, event: Event):
        if event.type == EventType.TRANSPORT_REQUESTED:
            # Schedule transport job
            job = self.transport_system.schedule_transport(
                from_module=event.data.get("from_module"),
                to_module=event.data.get("to_module"),
                resource=event.data.get("resource"),
                quantity=event.data.get("quantity", 0),
                distance=event.data.get("distance", 10)
            )
            if job:
                self.publish_event(EventType.TRANSPORT_STARTED, {"job": job})


class WasteStreamWrapper(SubsystemBase):
    """Wrapper for existing WasteStream to implement ISubsystem interface"""

    def __init__(self, name: str = "waste"):
        super().__init__(name)
        self.waste_stream = None

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        self.waste_stream = WasteStream()
        self.recycling_efficiency = config.get("recycling_efficiency", 0.75)

        # Subscribe to waste generation events
        event_bus.subscribe(EventType.TASK_COMPLETED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled or not self.waste_stream:
            return {}

        # Process recycling opportunities
        recycled_materials = {}
        for resource_type, efficiency in self.waste_stream.recyclable_materials.items():
            if resource_type in self.waste_stream.waste_inventory:
                amount = self.waste_stream.waste_inventory[resource_type]
                if amount > 0:
                    recycled = self.waste_stream.process_recycling(resource_type, amount)
                    if recycled > 0:
                        recycled_materials[resource_type] = recycled

        # Update metrics
        total_waste = self.waste_stream.get_total_waste()
        self.metrics["total_waste"] = total_waste
        self.metrics["recyclable_waste"] = sum(
            self.waste_stream.waste_inventory.get(r, 0) * eff
            for r, eff in self.waste_stream.recyclable_materials.items()
        )
        self.metrics["recycled_this_update"] = sum(recycled_materials.values())

        return {
            "recycled_materials": recycled_materials,
            "total_waste": total_waste
        }

    def handle_event(self, event: Event):
        if event.type == EventType.TASK_COMPLETED:
            # Add waste from completed task
            waste_data = event.data.get("waste", {})
            for waste_type, quantity in waste_data.items():
                if isinstance(waste_type, str):
                    # Convert string to ResourceType if needed
                    try:
                        waste_type = ResourceType[waste_type]
                    except KeyError:
                        continue
                self.waste_stream.add_waste(waste_type, quantity)


class ThermalSystemWrapper(SubsystemBase):
    """Wrapper for existing ThermalManagementSystem"""

    def __init__(self, name: str = "thermal"):
        super().__init__(name)
        self.thermal_system = None

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        thermal_config = {
            "ambient_temperature": config.get("ambient_temperature", 25),
            "enable_thermal_management": config.get("enable_thermal_management", True)
        }
        self.thermal_system = ThermalManagementSystem(thermal_config)

        # Subscribe to module activity events
        event_bus.subscribe(EventType.MODULE_BUSY, self.handle_event)
        event_bus.subscribe(EventType.MODULE_IDLE, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled or not self.thermal_system:
            return {}

        # Calculate thermal load from active modules
        module_states = context.modules
        total_heat = self.thermal_system.calculate_module_heat(module_states)

        # Check thermal constraints
        within_limits = self.thermal_system.check_thermal_constraints(total_heat)

        # Update metrics
        self.metrics["total_heat_generation"] = total_heat
        self.metrics["cooling_required"] = self.thermal_system.calculate_cooling_required(total_heat)
        self.metrics["within_thermal_limits"] = within_limits

        # Publish event if thermal limits exceeded
        if not within_limits:
            self.publish_event(EventType.THERMAL_LIMIT_REACHED, {
                "heat_generation": total_heat,
                "cooling_capacity": self.thermal_system.config.get("cooling_capacity", 1000)
            })

        return {
            "thermal_load": total_heat,
            "within_limits": within_limits
        }


class SoftwareSystemWrapper(SubsystemBase):
    """Wrapper for existing SoftwareProductionSystem"""

    def __init__(self, name: str = "software"):
        super().__init__(name)
        self.software_system = None

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        self.software_system = SoftwareProductionSystem()

        # Subscribe to software development tasks
        event_bus.subscribe(EventType.TASK_STARTED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled or not self.software_system:
            return {}

        # Develop software packages
        developed_packages = []
        for package_name in list(self.software_system.development_hours.keys()):
            if package_name not in self.software_system.software_library:
                self.software_system.develop_software(package_name, delta_time)
                if package_name in self.software_system.software_library:
                    developed_packages.append(package_name)

        # Calculate overall reliability
        avg_reliability = 0
        if self.software_system.software_library:
            avg_reliability = sum(
                pkg["reliability"] for pkg in self.software_system.software_library.values()
            ) / len(self.software_system.software_library)

        # Update metrics
        self.metrics["total_packages"] = len(self.software_system.software_library)
        self.metrics["packages_in_development"] = len(self.software_system.development_hours)
        self.metrics["average_reliability"] = avg_reliability
        self.metrics["developed_this_update"] = len(developed_packages)

        return {
            "developed_packages": developed_packages,
            "total_packages": len(self.software_system.software_library)
        }

    def handle_event(self, event: Event):
        if event.type == EventType.TASK_STARTED:
            # Check if task requires software
            software_required = event.data.get("software_required")
            if software_required and software_required not in self.software_system.software_library:
                # Start developing required software
                self.software_system.development_hours[software_required] = 0


class CleanroomWrapper(SubsystemBase):
    """Wrapper for CleanRoomEnvironment management"""

    def __init__(self, name: str = "cleanroom"):
        super().__init__(name)
        self.cleanrooms = {}

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        self.default_class = config.get("cleanroom_class", 1000)
        self.cleaning_interval = config.get("cleaning_interval_hours", 24)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Update all cleanrooms
        total_contamination = 0
        rooms_needing_cleaning = []

        for room_id, room in self.cleanrooms.items():
            room.update_contamination(delta_time)
            total_contamination += room.particle_count

            if room.time_since_cleaning > self.cleaning_interval:
                rooms_needing_cleaning.append(room_id)
                room.perform_cleaning()

        # Update metrics
        self.metrics["total_cleanrooms"] = len(self.cleanrooms)
        self.metrics["average_contamination"] = (
            total_contamination / len(self.cleanrooms) if self.cleanrooms else 0
        )
        self.metrics["rooms_cleaned"] = len(rooms_needing_cleaning)

        # Publish contamination events
        for room_id, room in self.cleanrooms.items():
            if room.particle_count > room.cleanroom_class * 10:
                self.publish_event(EventType.CONTAMINATION_DETECTED, {
                    "room_id": room_id,
                    "particle_count": room.particle_count,
                    "class": room.cleanroom_class
                })

        return {
            "rooms_cleaned": len(rooms_needing_cleaning),
            "average_contamination": self.metrics["average_contamination"]
        }

    def create_cleanroom(self, room_id: str, cleanroom_class: Optional[int] = None):
        """Create a new cleanroom"""
        if room_id not in self.cleanrooms:
            self.cleanrooms[room_id] = CleanRoomEnvironment(
                cleanroom_class or self.default_class
            )


class StorageSystemWrapper(SubsystemBase):
    """Wrapper for storage system functionality"""

    def __init__(self, name: str = "storage"):
        super().__init__(name)
        self.storage = defaultdict(float)
        self.max_volume = 15000  # m³
        self.max_weight = 10000  # tons

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        self.max_volume = config.get("max_storage_volume_m3", 15000)
        self.max_weight = config.get("max_storage_weight_tons", 10000)

        # Subscribe to resource events
        event_bus.subscribe(EventType.RESOURCE_PRODUCED, self.handle_event)
        event_bus.subscribe(EventType.RESOURCE_CONSUMED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Calculate current storage utilization
        total_volume = sum(self.storage.values()) * 0.001  # Rough conversion
        total_weight = sum(self.storage.values()) * 0.01   # Rough conversion

        volume_utilization = min(total_volume / self.max_volume, 1.0)
        weight_utilization = min(total_weight / self.max_weight, 1.0)

        # Update metrics
        self.metrics["volume_utilization"] = volume_utilization
        self.metrics["weight_utilization"] = weight_utilization
        self.metrics["total_items_stored"] = len(self.storage)
        self.metrics["total_quantity"] = sum(self.storage.values())

        # Check if storage is full
        if volume_utilization > 0.95 or weight_utilization > 0.95:
            self.publish_event(EventType.STORAGE_FULL, {
                "volume_utilization": volume_utilization,
                "weight_utilization": weight_utilization
            })

        return {
            "storage_utilization": max(volume_utilization, weight_utilization),
            "items_stored": len(self.storage)
        }

    def handle_event(self, event: Event):
        if event.type == EventType.RESOURCE_PRODUCED:
            resource = event.data.get("resource")
            quantity = event.data.get("quantity", 0)
            if resource:
                self.storage[resource] += quantity

        elif event.type == EventType.RESOURCE_CONSUMED:
            resource = event.data.get("resource")
            quantity = event.data.get("quantity", 0)
            if resource and self.storage[resource] >= quantity:
                self.storage[resource] -= quantity


class EnergySystemWrapper(SubsystemBase):
    """Wrapper for existing EnergySystem"""

    def __init__(self, name: str = "energy"):
        super().__init__(name)
        self.energy_system = None

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        super().initialize(config, event_bus)
        energy_config = {
            "initial_solar_capacity_kw": config.get("solar_capacity_kw", 100),
            "solar_panel_efficiency": config.get("panel_efficiency", 0.22),
            "battery_efficiency": config.get("battery_efficiency", 0.95),
            "latitude": config.get("latitude", 35.0),
            "average_cloud_cover": config.get("cloud_cover", 0.3),
            "enable_weather": config.get("enable_weather", True)
        }
        self.energy_system = EnergySystem(energy_config)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled or not self.energy_system:
            return {}

        hour = context.time % 24
        day = int(context.time / 24) % 365
        generated = self.energy_system.calculate_solar_generation(hour, day)

        # Metrics only — Factory owns battery accounting in hybrid mode
        self.metrics["solar_generation"] = generated
        self.metrics["battery_charge"] = self.energy_system.battery_charge_kwh
        capacity = max(self.energy_system.battery_capacity_kwh, 1e-9)
        self.metrics["battery_percentage"] = (
            self.energy_system.battery_charge_kwh / capacity
        )
        available = self.energy_system.battery_charge_kwh
        self.metrics["available_energy"] = available

        if self.metrics["battery_percentage"] < 0.1:
            self.publish_event(EventType.ENERGY_DEPLETED, {
                "battery_charge": self.energy_system.battery_charge_kwh,
                "percentage": self.metrics["battery_percentage"]
            })
        else:
            self.publish_event(EventType.ENERGY_AVAILABLE, {
                "available": available,
                "battery_percentage": self.metrics["battery_percentage"]
            })

        return {
            "energy_generated": generated,
            "energy_available": available
        }


# ===============================================================================
# MODULAR FACTORY
# ===============================================================================

class ModularFactory:
    """Modular subsystem host.

    Two modes:
    - Hybrid (preferred): ``hybrid_factory`` is a classic ``Factory`` with modular
      plugins hooked in. ``run_simulation`` drives real replication.
    - Sandbox: no hybrid backend — updates registered subsystems only. Useful for
      plugin experiments; does **not** claim factory replication.
    """

    def __init__(self, orchestrator: SubsystemOrchestrator = None,
                 config_manager: ConfigManager = None,
                 hybrid_factory: Optional[Factory] = None):
        # Reject mistaken ModularFactory(config_dict) calls early
        if orchestrator is not None and not isinstance(orchestrator, SubsystemOrchestrator):
            raise TypeError(
                "ModularFactory expects SubsystemOrchestrator, ConfigManager, "
                "and/or hybrid_factory=Factory. For replication use "
                "ModularFactoryBridge or create_factory_from_spec(); "
                "do not pass a config dict as the first argument."
            )

        self.orchestrator = orchestrator or SubsystemOrchestrator()
        self.config_manager = config_manager or ConfigManager()
        self.event_bus = self.orchestrator.event_bus
        self.hybrid_factory = hybrid_factory

        # Simulation state (sandbox mode)
        self.time = 0.0
        self.resources = defaultdict(float)
        self.modules = {}
        self.tasks = []
        self.metrics_history = []

        # Register default subsystems if none provided
        if not self.orchestrator.subsystems and hybrid_factory is None:
            self._register_default_subsystems()

    def _register_default_subsystems(self):
        """Register the default wrapped subsystems"""
        subsystems = [
            ("transport", TransportSystemWrapper()),
            ("waste", WasteStreamWrapper()),
            ("thermal", ThermalSystemWrapper()),
            ("software", SoftwareSystemWrapper()),
            ("cleanroom", CleanroomWrapper()),
            ("storage", StorageSystemWrapper()),
            ("energy", EnergySystemWrapper())
        ]

        for name, subsystem in subsystems:
            self.orchestrator.register_subsystem(name, subsystem)

        # Load default configs
        default_configs = self._create_default_configs()
        self.orchestrator.initialize_all(default_configs)

    def _create_default_configs(self) -> Dict[str, SubsystemConfig]:
        """Create default configurations from CONFIG"""
        return {
            "transport": SubsystemConfig({
                "agv_fleet_size": CONFIG.get("agv_fleet_size", 10),
                "enable_transport_time": CONFIG.get("enable_transport_time", True)
            }),
            "waste": SubsystemConfig({
                "recycling_efficiency": 0.75,
                "enable_waste_recycling": CONFIG.get("enable_waste_recycling", True)
            }),
            "thermal": SubsystemConfig({
                "ambient_temperature": CONFIG.get("ambient_temperature", 25),
                "enable_thermal_management": CONFIG.get("enable_thermal_management", True)
            }),
            "software": SubsystemConfig({
                "enable_software_production": CONFIG.get("enable_software_production", True)
            }),
            "cleanroom": SubsystemConfig({
                "cleanroom_class": CONFIG.get("cleanroom_class", 1000),
                "enable_contamination": CONFIG.get("enable_contamination", True)
            }),
            "storage": SubsystemConfig({
                "max_storage_volume_m3": CONFIG.get("max_storage_volume_m3", 15000),
                "max_storage_weight_tons": CONFIG.get("max_storage_weight_tons", 10000),
                "enable_storage_limits": CONFIG.get("enable_storage_limits", True)
            }),
            "energy": SubsystemConfig({
                "solar_capacity_kw": CONFIG.get("initial_solar_capacity_kw", 100),
                "panel_efficiency": CONFIG.get("solar_panel_efficiency", 0.22),
                "battery_efficiency": CONFIG.get("battery_efficiency", 0.95),
                "latitude": CONFIG.get("latitude", 35.0),
                "cloud_cover": CONFIG.get("average_cloud_cover", 0.3),
                "enable_weather": CONFIG.get("enable_weather", True)
            })
        }

    def run_simulation(self, max_hours: float = 10000, time_step: float = 0.1,
                       max_wall_time_seconds: float = 3600) -> Dict:
        """Run simulation.

        Hybrid mode delegates to the classic Factory replication engine.
        Sandbox mode only advances registered modular subsystems.
        """
        if self.hybrid_factory is not None:
            print("\n" + "=" * 80)
            print("HYBRID FACTORY SIMULATION (classic engine + modular plugins)")
            print("=" * 80)
            return self.hybrid_factory.run_simulation(
                max_hours=max_hours,
                max_wall_time_seconds=max_wall_time_seconds,
            )

        print("\n" + "=" * 80)
        print("MODULAR SUBSYSTEM SANDBOX (no replication engine)")
        print("=" * 80)
        print("Note: This path does not build factory modules. Use hybrid mode "
              "via create_factory_from_spec() or ModularFactoryBridge for replication.")

        # Set update strategy
        self.orchestrator.set_update_strategy(UpdateStrategy.DEPENDENCY)

        # Main simulation loop
        while self.time < max_hours:
            # Create context for this update
            context = SimulationContext(
                time=self.time,
                delta_time=time_step,
                resources=self.resources.copy(),
                modules=self.modules.copy(),
                tasks=self.tasks.copy()
            )

            # Update all subsystems
            update_results = self.orchestrator.update_all(time_step, context)

            # Process results and update state
            self._process_update_results(update_results)

            # Collect metrics periodically
            if int(self.time) % 10 == 0 and int(self.time) != int(self.time - time_step):
                self._collect_metrics()

            # Progress report
            if int(self.time) % 100 == 0 and int(self.time) != int(self.time - time_step):
                self._print_progress()

            self.time += time_step

            # Check completion conditions
            if self._check_completion():
                print(f"\n✅ Simulation completed successfully at {self.time:.1f} hours!")
                break

        # Final report
        return self._generate_final_report()

    def _process_update_results(self, results: Dict[str, Dict]):
        """Process results from subsystem updates"""
        for subsystem_name, result in results.items():
            if result and not result.get("error"):
                # Update resources from storage subsystem
                if subsystem_name == "storage" and "storage" in self.orchestrator.subsystems:
                    storage_wrapper = self.orchestrator.subsystems["storage"]
                    if hasattr(storage_wrapper, "storage"):
                        self.resources = storage_wrapper.storage.copy()

    def _collect_metrics(self):
        """Collect metrics from all subsystems"""
        metrics = {
            "time": self.time,
            "subsystems": self.orchestrator.get_metrics()
        }
        self.metrics_history.append(metrics)

    def _print_progress(self):
        """Print simulation progress"""
        metrics = self.orchestrator.get_metrics()
        print(f"\nTime: {self.time:.1f} hours ({self.time/24:.1f} days)")

        for name, m in metrics.items():
            if m:
                key_metrics = []
                for k, v in list(m.items())[:3]:  # Show top 3 metrics
                    if isinstance(v, float):
                        key_metrics.append(f"{k}: {v:.2f}")
                    else:
                        key_metrics.append(f"{k}: {v}")
                if key_metrics:
                    print(f"  {name}: {', '.join(key_metrics)}")

    def _check_completion(self) -> bool:
        """Check if simulation should complete"""
        # Simple completion check - can be customized
        return False

    def _generate_final_report(self) -> Dict:
        """Generate final simulation report"""
        return {
            "simulation_time": self.time,
            "final_metrics": self.orchestrator.get_metrics(),
            "final_state": self.orchestrator.get_state(),
            "metrics_history": self.metrics_history,
            "event_history": self.event_bus.get_history()[:100]  # Last 100 events
        }

    def add_custom_subsystem(self, name: str, subsystem: ISubsystem,
                            config: Optional[SubsystemConfig] = None,
                            dependencies: Optional[List[str]] = None):
        """Add a custom subsystem to the factory"""
        self.orchestrator.register_subsystem(name, subsystem, dependencies)
        if config:
            self.config_manager.set_subsystem_config(name, config)
            subsystem.initialize(config, self.event_bus)

    def set_update_strategy(self, strategy: UpdateStrategy):
        """Change how subsystems are updated"""
        self.orchestrator.set_update_strategy(strategy)

    def save_state(self, filepath: str):
        """Save current simulation state"""
        state = {
            "time": self.time,
            "resources": dict(self.resources),
            "modules": self.modules,
            "tasks": self.tasks,
            "subsystem_states": self.orchestrator.get_state(),
            "config": self.config_manager.base_config
        }
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2, default=str)

    def load_state(self, filepath: str):
        """Load simulation state"""
        with open(filepath, 'r') as f:
            state = json.load(f)

        self.time = state["time"]
        self.resources = defaultdict(float, state["resources"])
        self.modules = state["modules"]
        self.tasks = state["tasks"]
        self.orchestrator.set_state(state["subsystem_states"])


# ===============================================================================
# BACKWARD COMPATIBILITY BRIDGE
# ===============================================================================

class ModularFactoryBridge:
    """Bridge to run classic Factory with modular subsystem plugins.

    Custom implementations from ``subsystem_implementations`` are registered as
    event-driven plugins. When a plugin exposes a Factory-compatible legacy object
    (e.g. ``.transport_system``, ``.energy_system``), that object replaces the
    Factory's corresponding subsystem. Otherwise the plugin only receives update
    hooks and events alongside the real engine.
    """

    # Map spec roles → Factory attribute + optional legacy attr on plugin
    ROLE_MAP = {
        "transport": ("transport_system", "transport_system"),
        "waste": ("waste_stream", "waste_stream"),
        "thermal": ("thermal_system", "thermal_system"),
        "software": ("software_system", "software_system"),
        "energy": ("energy_system", "energy_system"),
        "cleanroom": ("cleanroom", "cleanroom"),
        "storage": ("storage", "storage"),
    }

    def __init__(
        self,
        config: Optional[Dict] = None,
        spec_dict: Optional[Dict] = None,
        resource_enum=None,
        recipes: Optional[Dict] = None,
        module_specs: Optional[Dict] = None,
        subsystem_implementations: Optional[Dict[str, str]] = None,
        subsystem_data: Optional[Dict[str, Dict]] = None,
    ):
        self.config = config or CONFIG
        self.spec_dict = spec_dict
        self.resource_enum = resource_enum
        self.recipes = recipes
        self.module_specs = module_specs
        self.subsystem_implementations = subsystem_implementations or {}
        self.subsystem_data = subsystem_data or {}

        # Sandbox ModularFactory only for orchestrator/event bus (no default register
        # if we will plug into hybrid — pass empty orchestrator then register plugins)
        self.modular_factory = ModularFactory(
            orchestrator=SubsystemOrchestrator(),
            config_manager=ConfigManager(base_config=self.config),
            hybrid_factory=None,
        )
        # Avoid empty sandbox defaults when we intentionally start clean
        self.modular_factory.orchestrator.subsystems.clear()
        self.original_factory = None
        self._plugin_subsystems: List[Any] = []

    def create_hybrid_factory(self) -> Factory:
        """Create a hybrid factory that uses modular subsystems/plugins."""
        self.original_factory = Factory(
            self.config,
            spec_dict=self.spec_dict,
            resource_enum=self.resource_enum,
        )

        # Apply recipes/module specs from spec when provided
        if self.recipes is not None:
            # Factory methods close over module-level RECIPES; also set instance attrs
            self.original_factory.recipes = self.recipes  # type: ignore
        if self.module_specs is not None:
            self.original_factory.module_specs = self.module_specs  # type: ignore

        self._wire_plugins()
        return self.original_factory

    def _default_configs(self) -> Dict[str, SubsystemConfig]:
        return {
            "transport": SubsystemConfig({
                "agv_fleet_size": self.config.get("agv_fleet_size", 10),
                "enable_transport_time": self.config.get("enable_transport_time", True),
            }),
            "waste": SubsystemConfig({
                "recycling_efficiency": 0.75,
                "enable_waste_recycling": self.config.get("enable_waste_recycling", True),
            }),
            "thermal": SubsystemConfig({
                "ambient_temperature": self.config.get("ambient_temperature", 25),
                "enable_thermal_management": self.config.get("enable_thermal_management", True),
            }),
            "software": SubsystemConfig({
                "enable_software_production": self.config.get("enable_software_production", True),
            }),
            "cleanroom": SubsystemConfig({
                "cleanroom_class": self.config.get("cleanroom_class", 1000),
                "enable_contamination": self.config.get("enable_contamination", True),
            }),
            "storage": SubsystemConfig({
                "max_storage_volume_m3": self.config.get("max_storage_volume_m3", 15000),
                "max_storage_weight_tons": self.config.get("max_storage_weight_tons", 10000),
                "enable_storage_limits": self.config.get("enable_storage_limits", True),
            }),
            "energy": SubsystemConfig({
                "solar_capacity_kw": self.config.get("initial_solar_capacity_kw", 100),
                "panel_efficiency": self.config.get("solar_panel_efficiency", 0.22),
                "battery_efficiency": self.config.get("battery_efficiency", 0.95),
                "latitude": self.config.get("latitude", 35.0),
                "cloud_cover": self.config.get("average_cloud_cover", 0.3),
                "enable_weather": self.config.get("enable_weather", True),
            }),
        }

    def _wire_plugins(self):
        """Register wrappers + custom implementations and hook into Factory step."""
        event_bus = self.modular_factory.event_bus
        defaults = self._default_configs()
        wrappers = {
            "transport": TransportSystemWrapper(),
            "waste": WasteStreamWrapper(),
            "thermal": ThermalSystemWrapper(),
            "software": SoftwareSystemWrapper(),
            "cleanroom": CleanroomWrapper(),
            "storage": StorageSystemWrapper(),
            "energy": EnergySystemWrapper(),
        }

        # Start from Factory's existing subsystems for roles we do not replace
        role_to_legacy = {
            "transport": self.original_factory.transport_system,
            "waste": self.original_factory.waste_stream,
            "thermal": self.original_factory.thermal_system,
            "software": self.original_factory.software_system,
            "energy": self.original_factory.energy_system,
        }

        plugins: List[Any] = []

        # Always register default wrappers as plugins (reuse Factory objects where possible)
        for role, wrapper in wrappers.items():
            cfg = defaults.get(role, SubsystemConfig({"enabled": True}))
            if role in self.subsystem_data:
                cfg = SubsystemConfig({**cfg.config, **self.subsystem_data[role]})
            wrapper.initialize(cfg, event_bus)
            # Prefer Factory's already-constructed legacy objects
            legacy_attr = self.ROLE_MAP.get(role, (None, None))[1]
            if legacy_attr and role in role_to_legacy and hasattr(wrapper, legacy_attr):
                setattr(wrapper, legacy_attr, role_to_legacy[role])
            self.modular_factory.orchestrator.register_subsystem(role, wrapper)
            plugins.append(wrapper)

        # Substitute / add custom implementations from spec
        for role, impl_name in self.subsystem_implementations.items():
            if impl_name not in SubsystemRegistry.list_available():
                raise ValueError(
                    f"Unknown subsystem implementation '{impl_name}' for role '{role}'. "
                    f"Available: {sorted(SubsystemRegistry.list_available())}"
                )
            custom = SubsystemRegistry.create(impl_name)
            custom_cfg_data = dict(defaults.get(role, SubsystemConfig({})).config)
            if role in self.subsystem_data:
                custom_cfg_data.update(self.subsystem_data[role])
            custom_cfg = SubsystemConfig(custom_cfg_data)
            custom.initialize(custom_cfg, event_bus)

            # Replace default wrapper registration for this role
            if role in self.modular_factory.orchestrator.subsystems:
                self.modular_factory.orchestrator.unregister_subsystem(role)
            self.modular_factory.orchestrator.register_subsystem(role, custom)
            plugins = [p for p in plugins if getattr(p, "name", None) != role]
            plugins.append(custom)

            # If custom exposes a Factory-compatible legacy object, substitute it
            factory_attr, legacy_attr = self.ROLE_MAP.get(role, (None, None))
            if factory_attr and legacy_attr and hasattr(custom, legacy_attr):
                legacy_obj = getattr(custom, legacy_attr)
                if legacy_obj is not None and hasattr(self.original_factory, factory_attr):
                    setattr(self.original_factory, factory_attr, legacy_obj)
                    logger_msg = f"Substituted Factory.{factory_attr} from {impl_name}"
                    print(f"  ✓ {logger_msg}")

        self._plugin_subsystems = list(self.modular_factory.orchestrator.subsystems.values())

        # Hook plugin updates into Factory.simulate_step (actual step method name)
        step_attr = "simulate_step" if hasattr(self.original_factory, "simulate_step") else "simulation_step"
        original_step = getattr(self.original_factory, step_attr)

        def wrapped_step(time_step):
            storage = self.original_factory.storage
            resources = dict(storage.current_inventory) if hasattr(storage, "current_inventory") else {}
            context = SimulationContext(
                time=self.original_factory.time,
                delta_time=time_step,
                resources=resources,
                modules=self.original_factory.module_states,
                tasks=list(self.original_factory.task_queue),
            )
            for plugin in self._plugin_subsystems:
                try:
                    plugin.update(time_step, context)
                except Exception as exc:  # keep engine alive if a plugin fails
                    print(f"  Warning: plugin {getattr(plugin, 'name', plugin)} update failed: {exc}")
            self.modular_factory.event_bus.process_events()
            return original_step(time_step)

        setattr(self.original_factory, step_attr, wrapped_step)


# Register all wrapper subsystems
SubsystemRegistry.register("transport_wrapper", TransportSystemWrapper)
SubsystemRegistry.register("waste_wrapper", WasteStreamWrapper)
SubsystemRegistry.register("thermal_wrapper", ThermalSystemWrapper)
SubsystemRegistry.register("software_wrapper", SoftwareSystemWrapper)
SubsystemRegistry.register("cleanroom_wrapper", CleanroomWrapper)
SubsystemRegistry.register("storage_wrapper", StorageSystemWrapper)
SubsystemRegistry.register("energy_wrapper", EnergySystemWrapper)


if __name__ == "__main__":
    # Demonstration of modular factory
    print("Modular Factory Adapter Demonstration")
    print("=" * 60)

    # Create modular factory
    factory = ModularFactory()

    # Add a custom subsystem
    from .modular_framework import AdaptiveTransportSubsystem
    custom_transport = AdaptiveTransportSubsystem("custom_transport")
    factory.add_custom_subsystem(
        "custom_transport",
        custom_transport,
        SubsystemConfig({"enabled": True})
    )

    # Run short simulation
    print("\nRunning modular factory simulation...")
    result = factory.run_simulation(max_hours=10, time_step=0.1)

    print(f"\n📊 Simulation completed at {result['simulation_time']:.1f} hours")
    print("\nFinal subsystem metrics:")
    for name, metrics in result["final_metrics"].items():
        if metrics:
            print(f"  {name}: {list(metrics.keys())[:3]}")

    # Demonstrate hybrid mode
    print("\n" + "=" * 60)
    print("Hybrid Factory Mode (using existing Factory with modular subsystems)")

    bridge = ModularFactoryBridge()
    hybrid_factory = bridge.create_hybrid_factory()

    print(f"✅ Created hybrid factory with {len(hybrid_factory.modules)} modules")
    print(f"   Transport system: {'✓' if hybrid_factory.transport_system else '✗'}")
    print(f"   Waste system: {'✓' if hybrid_factory.waste_stream else '✗'}")
    print(f"   Thermal system: {'✓' if hybrid_factory.thermal_system else '✗'}")
    print(f"   Software system: {'✓' if hybrid_factory.software_system else '✗'}")