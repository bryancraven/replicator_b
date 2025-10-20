#!/usr/bin/env python3
"""
Modular Framework for Ultra-Realistic Factory Simulation

This module provides a flexible, extensible architecture for subsystems that can be
easily swapped, parallelized, and reconfigured without modifying core simulation code.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Callable, Type
from collections import defaultdict, deque
from enum import Enum
import json
import time
import threading
from queue import Queue
import logging

# Configure module logger
logger = logging.getLogger(__name__)


# ===============================================================================
# CORE INTERFACES
# ===============================================================================

class SubsystemConfig:
    """Base configuration class for subsystems"""
    def __init__(self, config_dict: Dict[str, Any] = None):
        self.config = config_dict or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value with default"""
        return self.config.get(key, default)

    def merge(self, other: 'SubsystemConfig'):
        """Merge another config into this one"""
        self.config.update(other.config)


@dataclass
class SimulationContext:
    """Context passed to subsystems during updates"""
    time: float
    delta_time: float
    resources: Dict[str, float] = field(default_factory=dict)
    modules: Dict[str, Any] = field(default_factory=dict)
    tasks: List[Any] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> 'SimulationContext':
        """Create an efficient copy of the context (shallow copy of immutable data)"""
        return SimulationContext(
            time=self.time,  # Immutable
            delta_time=self.delta_time,  # Immutable
            resources=self.resources.copy(),  # Shallow dict copy (sufficient for parallel subsystems)
            modules=self.modules.copy(),  # Shallow dict copy
            tasks=self.tasks[:],  # List slice copy
            metrics=self.metrics.copy()  # Shallow dict copy
        )


# ===============================================================================
# EVENT SYSTEM
# ===============================================================================

class EventType(Enum):
    """Standard event types for inter-subsystem communication"""
    # Resource events
    RESOURCE_PRODUCED = "resource_produced"
    RESOURCE_CONSUMED = "resource_consumed"
    RESOURCE_REQUESTED = "resource_requested"

    # Module events
    MODULE_CREATED = "module_created"
    MODULE_FAILED = "module_failed"
    MODULE_REPAIRED = "module_repaired"
    MODULE_BUSY = "module_busy"
    MODULE_IDLE = "module_idle"

    # Task events
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_BLOCKED = "task_blocked"
    TASK_FAILED = "task_failed"

    # Transport events
    TRANSPORT_REQUESTED = "transport_requested"
    TRANSPORT_STARTED = "transport_started"
    TRANSPORT_COMPLETED = "transport_completed"

    # System events
    ENERGY_AVAILABLE = "energy_available"
    ENERGY_DEPLETED = "energy_depleted"
    THERMAL_LIMIT_REACHED = "thermal_limit_reached"
    STORAGE_FULL = "storage_full"
    CONTAMINATION_DETECTED = "contamination_detected"

    # Custom events
    CUSTOM = "custom"


@dataclass
class Event:
    """Event for inter-subsystem communication"""
    type: EventType
    source: str  # Subsystem name that generated the event
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def __str__(self):
        return f"Event({self.type.value} from {self.source} at {self.timestamp:.2f})"


class EventBus:
    """Central event bus for publish/subscribe communication (thread-safe)"""

    def __init__(self, max_history: int = 1000, max_queue_size: int = 10000):
        """
        Initialize event bus with backpressure support.

        Args:
            max_history: Maximum number of events to keep in history
            max_queue_size: Maximum size of event queue (0 = unbounded)
        """
        self.subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self.event_queue: Queue = Queue(maxsize=max_queue_size) if max_queue_size > 0 else Queue()
        self.event_history: deque[Event] = deque(maxlen=max_history)
        self.max_history = max_history
        self.max_queue_size = max_queue_size
        self.dropped_events = 0
        self._subscribers_lock = threading.Lock()  # Thread safety for subscribers

    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Subscribe to events of a specific type (thread-safe)"""
        with self._subscribers_lock:
            self.subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: EventType, handler: Callable):
        """Unsubscribe from events (thread-safe)"""
        with self._subscribers_lock:
            if handler in self.subscribers[event_type]:
                self.subscribers[event_type].remove(handler)

    def publish(self, event: Event):
        """
        Publish an event to all subscribers.

        If queue is full, the event is dropped and logged.
        Raises EventQueueOverflowError if drop rate is critical.
        """
        from queue import Full
        try:
            self.event_queue.put_nowait(event)
            self.event_history.append(event)  # deque automatically maintains maxlen
        except Full:
            self.dropped_events += 1

            # Import constant from self_replicating_factory_sim if available, else use default
            try:
                from self_replicating_factory_sim import EVENT_QUEUE_DROP_LOG_INTERVAL
                log_interval = EVENT_QUEUE_DROP_LOG_INTERVAL
            except ImportError:
                log_interval = 100  # Default fallback

            # Log at regular intervals
            if self.dropped_events % log_interval == 1:
                logger.warning(
                    f"Event queue full (size={self.max_queue_size}), "
                    f"dropped {self.dropped_events} events total. "
                    f"Latest dropped: {event}"
                )

            # Raise exception if drop rate is critical (>10% of queue size)
            if self.dropped_events > self.max_queue_size * 0.1:
                from exceptions import EventQueueOverflowError
                raise EventQueueOverflowError(
                    self.event_queue.qsize(),
                    self.max_queue_size
                )

    def process_events(self):
        """Process all queued events (thread-safe)"""
        while not self.event_queue.empty():
            event = self.event_queue.get()

            # Get handler list with lock
            with self._subscribers_lock:
                handlers = list(self.subscribers[event.type])  # Copy to avoid modification during iteration
                custom_handlers = list(self.subscribers.get(EventType.CUSTOM, []))

            # Call handlers without holding lock
            for handler in handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {event}: {e}", exc_info=True)

            # Also notify generic subscribers
            for handler in custom_handlers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in custom handler for {event}: {e}", exc_info=True)

    def get_history(self, event_type: Optional[EventType] = None,
                    source: Optional[str] = None) -> List[Event]:
        """Get event history with optional filtering"""
        history = list(self.event_history)
        if event_type:
            history = [e for e in history if e.type == event_type]
        if source:
            history = [e for e in history if e.source == source]
        return history

    def get_metrics(self) -> Dict[str, Any]:
        """Get event bus metrics"""
        return {
            "queue_size": self.event_queue.qsize(),
            "max_queue_size": self.max_queue_size,
            "history_size": len(self.event_history),
            "max_history_size": self.max_history,
            "dropped_events": self.dropped_events,
            "subscriber_count": sum(len(handlers) for handlers in self.subscribers.values())
        }


# ===============================================================================
# SUBSYSTEM INTERFACES
# ===============================================================================

class ISubsystem(ABC):
    """Abstract interface that all subsystems must implement"""

    @abstractmethod
    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        """Initialize the subsystem with configuration"""
        pass

    @abstractmethod
    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        """Update the subsystem for one time step

        Returns:
            Dict containing any state changes or outputs
        """
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics from the subsystem"""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current internal state for serialization"""
        pass

    @abstractmethod
    def set_state(self, state: Dict[str, Any]):
        """Restore internal state from serialization"""
        pass

    def handle_event(self, event: Event):
        """Handle events from other subsystems"""
        pass

    def validate(self) -> List[str]:
        """Validate subsystem configuration and state

        Returns:
            List of validation errors (empty if valid)
        """
        return []

    def reset(self):
        """Reset the subsystem to initial state"""
        pass

    def shutdown(self):
        """Clean shutdown of the subsystem"""
        pass


class SubsystemBase(ISubsystem):
    """Base implementation with common functionality"""

    def __init__(self, name: str):
        self.name = name
        self.config: Optional[SubsystemConfig] = None
        self.event_bus: Optional[EventBus] = None
        self.enabled = True
        self.metrics = {}
        self.state = {}

    def initialize(self, config: SubsystemConfig, event_bus: EventBus):
        """Default initialization"""
        self.config = config
        self.event_bus = event_bus
        self.enabled = config.get("enabled", True)

    def publish_event(self, event_type: EventType, data: Dict[str, Any]):
        """Helper to publish events"""
        if self.event_bus:
            event = Event(type=event_type, source=self.name, data=data)
            self.event_bus.publish(event)

    def get_metrics(self) -> Dict[str, Any]:
        """Return current metrics"""
        return self.metrics.copy()

    def get_state(self) -> Dict[str, Any]:
        """Return current state"""
        return self.state.copy()

    def set_state(self, state: Dict[str, Any]):
        """Restore state"""
        self.state = state.copy()


# ===============================================================================
# SUBSYSTEM ORCHESTRATOR
# ===============================================================================

class UpdateStrategy(Enum):
    """Different strategies for updating subsystems"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PRIORITY = "priority"
    DEPENDENCY = "dependency"


class SubsystemOrchestrator:
    """Manages and coordinates all subsystems"""

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.subsystems: Dict[str, ISubsystem] = {}
        self.event_bus = event_bus or EventBus()
        self.update_order: List[str] = []
        self.dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.update_strategy = UpdateStrategy.SEQUENTIAL
        self.parallel_executor = None

    def register_subsystem(self, name: str, subsystem: ISubsystem,
                          dependencies: List[str] = None):
        """Register a subsystem with optional dependencies"""
        if name in self.subsystems:
            raise ValueError(f"Subsystem '{name}' already registered")

        self.subsystems[name] = subsystem
        if dependencies:
            self.dependencies[name] = set(dependencies)

        # Rebuild update order
        self._rebuild_update_order()

    def unregister_subsystem(self, name: str):
        """Remove a subsystem"""
        if name in self.subsystems:
            self.subsystems[name].shutdown()
            del self.subsystems[name]
            if name in self.dependencies:
                del self.dependencies[name]
            self._rebuild_update_order()

    def _rebuild_update_order(self):
        """Rebuild the update order based on dependencies"""
        # Simple topological sort
        visited = set()
        order = []

        def visit(name):
            if name in visited:
                return
            visited.add(name)
            for dep in self.dependencies.get(name, []):
                if dep in self.subsystems:
                    visit(dep)
            order.append(name)

        for name in self.subsystems:
            visit(name)

        self.update_order = order

    def initialize_all(self, configs: Dict[str, SubsystemConfig]):
        """Initialize all subsystems with their configs"""
        for name, subsystem in self.subsystems.items():
            config = configs.get(name, SubsystemConfig())
            subsystem.initialize(config, self.event_bus)

    def update_all(self, delta_time: float, context: SimulationContext) -> Dict[str, Dict]:
        """Update all subsystems according to strategy"""
        results = {}

        if self.update_strategy == UpdateStrategy.SEQUENTIAL:
            results = self._update_sequential(delta_time, context)
        elif self.update_strategy == UpdateStrategy.PARALLEL:
            results = self._update_parallel(delta_time, context)
        elif self.update_strategy == UpdateStrategy.DEPENDENCY:
            results = self._update_dependency_order(delta_time, context)

        # Process all events generated during updates
        self.event_bus.process_events()

        return results

    def _update_sequential(self, delta_time: float, context: SimulationContext) -> Dict:
        """Update subsystems one at a time"""
        results = {}
        for name in self.update_order:
            if name in self.subsystems:
                subsystem = self.subsystems[name]
                try:
                    results[name] = subsystem.update(delta_time, context)
                except Exception as e:
                    logger.error(f"Error updating subsystem '{name}': {e}", exc_info=True)
                    results[name] = {"error": str(e)}
        return results

    def _update_parallel(self, delta_time: float, context: SimulationContext) -> Dict:
        """Update independent subsystems in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = {}

        # Group subsystems by dependency level
        levels = self._get_dependency_levels()

        with ThreadPoolExecutor(max_workers=4) as executor:
            for level in levels:
                # Update all subsystems at this level in parallel
                futures = {}
                for name in level:
                    if name in self.subsystems:
                        # Each subsystem gets its own context copy
                        ctx_copy = context.copy()
                        future = executor.submit(
                            self.subsystems[name].update,
                            delta_time,
                            ctx_copy
                        )
                        futures[future] = name

                # Wait for all at this level to complete
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        results[name] = future.result()
                    except Exception as e:
                        logger.error(f"Error updating subsystem '{name}' in parallel: {e}", exc_info=True)
                        results[name] = {"error": str(e)}

        return results

    def _update_dependency_order(self, delta_time: float, context: SimulationContext) -> Dict:
        """Update in strict dependency order"""
        return self._update_sequential(delta_time, context)

    def _get_dependency_levels(self) -> List[List[str]]:
        """Group subsystems by dependency level for parallel execution"""
        levels = []
        remaining = set(self.subsystems.keys())
        satisfied = set()

        while remaining:
            level = []
            for name in remaining:
                deps = self.dependencies.get(name, set())
                if deps.issubset(satisfied):
                    level.append(name)

            if not level:
                # Circular dependency or missing subsystem
                level = list(remaining)

            levels.append(level)
            satisfied.update(level)
            remaining -= set(level)

        return levels

    def get_metrics(self) -> Dict[str, Dict]:
        """Get metrics from all subsystems"""
        return {name: subsystem.get_metrics()
                for name, subsystem in self.subsystems.items()}

    def get_state(self) -> Dict[str, Dict]:
        """Get state from all subsystems for serialization"""
        return {name: subsystem.get_state()
                for name, subsystem in self.subsystems.items()}

    def set_state(self, state: Dict[str, Dict]):
        """Restore state to all subsystems"""
        for name, subsystem_state in state.items():
            if name in self.subsystems:
                self.subsystems[name].set_state(subsystem_state)

    def set_update_strategy(self, strategy: UpdateStrategy):
        """Change the update strategy"""
        self.update_strategy = strategy

    def validate_all(self) -> Dict[str, List[str]]:
        """Validate all subsystems"""
        errors = {}
        for name, subsystem in self.subsystems.items():
            subsystem_errors = subsystem.validate()
            if subsystem_errors:
                errors[name] = subsystem_errors
        return errors


# ===============================================================================
# SUBSYSTEM REGISTRY AND FACTORY
# ===============================================================================

class SubsystemRegistry:
    """Registry for available subsystem implementations"""

    _registry: Dict[str, Type[ISubsystem]] = {}

    @classmethod
    def register(cls, name: str, subsystem_class: Type[ISubsystem]):
        """Register a subsystem implementation"""
        cls._registry[name] = subsystem_class

    @classmethod
    def create(cls, name: str, *args, **kwargs) -> ISubsystem:
        """Create a subsystem instance"""
        if name not in cls._registry:
            raise ValueError(f"Unknown subsystem type: {name}")
        return cls._registry[name](*args, **kwargs)

    @classmethod
    def list_available(cls) -> List[str]:
        """List all registered subsystem types"""
        return list(cls._registry.keys())

    @classmethod
    def get_class(cls, name: str) -> Type[ISubsystem]:
        """Get the class for a subsystem type"""
        return cls._registry.get(name)


# ===============================================================================
# CONFIGURATION MANAGEMENT
# ===============================================================================

class ConfigManager:
    """Manages hierarchical configuration for all subsystems"""

    def __init__(self, base_config: Dict[str, Any] = None):
        self.base_config = base_config or {}
        self.subsystem_configs: Dict[str, SubsystemConfig] = {}
        self.profiles: Dict[str, Dict] = {}

    def load_from_file(self, filepath: str):
        """Load configuration from JSON file"""
        with open(filepath, 'r') as f:
            config = json.load(f)
        self.base_config = config.get("base", {})

        # Load subsystem configs
        for name, config_dict in config.get("subsystems", {}).items():
            self.subsystem_configs[name] = SubsystemConfig(config_dict)

        # Load profiles
        self.profiles = config.get("profiles", {})

    def save_to_file(self, filepath: str):
        """Save configuration to JSON file"""
        config = {
            "base": self.base_config,
            "subsystems": {name: cfg.config
                          for name, cfg in self.subsystem_configs.items()},
            "profiles": self.profiles
        }
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)

    def get_subsystem_config(self, name: str) -> SubsystemConfig:
        """Get configuration for a specific subsystem"""
        if name not in self.subsystem_configs:
            self.subsystem_configs[name] = SubsystemConfig()
        return self.subsystem_configs[name]

    def set_subsystem_config(self, name: str, config: SubsystemConfig):
        """Set configuration for a subsystem"""
        self.subsystem_configs[name] = config

    def apply_profile(self, profile_name: str):
        """Apply a configuration profile"""
        if profile_name not in self.profiles:
            raise ValueError(f"Unknown profile: {profile_name}")

        profile = self.profiles[profile_name]

        # Merge base config
        if "base" in profile:
            self.base_config.update(profile["base"])

        # Merge subsystem configs
        for name, config_dict in profile.get("subsystems", {}).items():
            if name not in self.subsystem_configs:
                self.subsystem_configs[name] = SubsystemConfig()
            self.subsystem_configs[name].merge(SubsystemConfig(config_dict))

    def create_profile(self, name: str, description: str = ""):
        """Create a new profile from current configuration"""
        self.profiles[name] = {
            "description": description,
            "base": self.base_config.copy(),
            "subsystems": {name: cfg.config.copy()
                          for name, cfg in self.subsystem_configs.items()}
        }

    def get_all_configs(self) -> Dict[str, SubsystemConfig]:
        """Get all subsystem configurations"""
        return self.subsystem_configs.copy()


# ===============================================================================
# SUBSYSTEM CONTAINER (Dependency Injection)
# ===============================================================================

class SubsystemContainer:
    """Dependency injection container for subsystems"""

    def __init__(self):
        self.bindings: Dict[str, Callable] = {}
        self.singletons: Dict[str, ISubsystem] = {}
        self.orchestrator = SubsystemOrchestrator()
        self.config_manager = ConfigManager()

    def bind(self, name: str, factory: Callable[[], ISubsystem], singleton: bool = True):
        """Bind a subsystem factory"""
        self.bindings[name] = (factory, singleton)

    def bind_class(self, name: str, subsystem_class: Type[ISubsystem],
                   singleton: bool = True):
        """Bind a subsystem class"""
        self.bind(name, lambda: subsystem_class(name), singleton)

    def resolve(self, name: str) -> ISubsystem:
        """Resolve a subsystem instance"""
        if name not in self.bindings:
            raise ValueError(f"No binding for subsystem: {name}")

        factory, is_singleton = self.bindings[name]

        if is_singleton:
            if name not in self.singletons:
                self.singletons[name] = factory()
            return self.singletons[name]
        else:
            return factory()

    def resolve_all(self) -> Dict[str, ISubsystem]:
        """Resolve all bound subsystems"""
        return {name: self.resolve(name) for name in self.bindings}

    def build_factory(self, config_file: Optional[str] = None) -> 'ModularFactory':
        """Build a complete factory with all subsystems"""
        from modular_factory_adapter import ModularFactory

        if config_file:
            self.config_manager.load_from_file(config_file)

        # Resolve all subsystems
        subsystems = self.resolve_all()

        # Register with orchestrator
        for name, subsystem in subsystems.items():
            deps = self.bindings[name][1] if len(self.bindings[name]) > 2 else []
            self.orchestrator.register_subsystem(name, subsystem, deps)

        # Initialize all subsystems
        self.orchestrator.initialize_all(self.config_manager.get_all_configs())

        # Create and return factory
        return ModularFactory(self.orchestrator, self.config_manager)


# ===============================================================================
# TESTING UTILITIES
# ===============================================================================

class MockSubsystem(SubsystemBase):
    """Mock subsystem for testing"""

    def __init__(self, name: str, update_return: Dict = None):
        super().__init__(name)
        self.update_return = update_return or {}
        self.update_count = 0
        self.events_received = []

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        self.update_count += 1
        self.metrics["update_count"] = self.update_count
        return self.update_return

    def handle_event(self, event: Event):
        self.events_received.append(event)


class SubsystemRecorder:
    """Records subsystem interactions for debugging and testing"""

    def __init__(self, subsystem: ISubsystem):
        self.subsystem = subsystem
        self.call_history = []

    def __getattr__(self, name):
        """Proxy all calls and record them"""
        attr = getattr(self.subsystem, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                self.call_history.append({
                    "method": name,
                    "args": args,
                    "kwargs": kwargs,
                    "timestamp": time.time()
                })
                return attr(*args, **kwargs)
            return wrapper
        return attr

    def get_history(self) -> List[Dict]:
        """Get the call history"""
        return self.call_history.copy()


# ===============================================================================
# EXAMPLE CUSTOM SUBSYSTEMS
# ===============================================================================

class AdaptiveTransportSubsystem(SubsystemBase):
    """Example adaptive transport system that learns optimal routes"""

    def __init__(self, name: str = "adaptive_transport"):
        super().__init__(name)
        self.route_performance = defaultdict(list)
        self.active_transports = {}

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Analyze route performance and adapt
        completed = 0
        for transport_id, transport in list(self.active_transports.items()):
            transport["time_remaining"] -= delta_time
            if transport["time_remaining"] <= 0:
                # Record performance
                route_key = f"{transport['from']}->{transport['to']}"
                actual_time = transport["elapsed_time"]
                self.route_performance[route_key].append(actual_time)

                # Complete transport
                self.publish_event(
                    EventType.TRANSPORT_COMPLETED,
                    {"transport_id": transport_id, "route": route_key}
                )
                del self.active_transports[transport_id]
                completed += 1
            else:
                transport["elapsed_time"] += delta_time

        self.metrics["active_transports"] = len(self.active_transports)
        self.metrics["completed_this_update"] = completed

        return {"completed": completed}

    def handle_event(self, event: Event):
        """Handle transport requests"""
        if event.type == EventType.TRANSPORT_REQUESTED:
            # Create new transport with adaptive timing
            transport_id = f"transport_{time.time()}"
            route_key = f"{event.data['from']}->{event.data['to']}"

            # Estimate time based on history
            if route_key in self.route_performance:
                avg_time = sum(self.route_performance[route_key]) / len(self.route_performance[route_key])
                estimated_time = avg_time * 0.9  # Optimize over time
            else:
                estimated_time = 10.0  # Default

            self.active_transports[transport_id] = {
                "from": event.data["from"],
                "to": event.data["to"],
                "time_remaining": estimated_time,
                "elapsed_time": 0
            }

            self.publish_event(
                EventType.TRANSPORT_STARTED,
                {"transport_id": transport_id, "estimated_time": estimated_time}
            )


class MLQualityControlSubsystem(SubsystemBase):
    """Example ML-based quality control that predicts defects"""

    def __init__(self, name: str = "ml_quality"):
        super().__init__(name)
        self.defect_history = []
        self.prediction_model = {"base_rate": 0.05}  # Simple model

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Analyze current production context
        production_rate = len([t for t in context.tasks if t.get("status") == "active"])

        # Predict defect probability (simplified)
        stress_factor = production_rate / 10.0  # Higher rate = more defects
        defect_prob = self.prediction_model["base_rate"] * (1 + stress_factor)

        # Update model based on history
        if len(self.defect_history) > 100:
            recent_rate = sum(self.defect_history[-100:]) / 100
            self.prediction_model["base_rate"] = 0.8 * self.prediction_model["base_rate"] + 0.2 * recent_rate

        self.metrics["predicted_defect_rate"] = defect_prob
        self.metrics["model_base_rate"] = self.prediction_model["base_rate"]

        return {"defect_probability": defect_prob}

    def handle_event(self, event: Event):
        """Track actual defects to improve model"""
        if event.type == EventType.TASK_FAILED:
            if event.data.get("reason") == "quality_failure":
                self.defect_history.append(1)
        elif event.type == EventType.TASK_COMPLETED:
            self.defect_history.append(0)


# Register example subsystems
SubsystemRegistry.register("adaptive_transport", AdaptiveTransportSubsystem)
SubsystemRegistry.register("ml_quality", MLQualityControlSubsystem)
SubsystemRegistry.register("mock", MockSubsystem)


if __name__ == "__main__":
    # Demonstration of the modular framework
    print("Modular Framework for Ultra-Realistic Factory Simulation")
    print("=" * 60)

    # Create event bus and orchestrator
    event_bus = EventBus()
    orchestrator = SubsystemOrchestrator(event_bus)

    # Create and register example subsystems
    transport = AdaptiveTransportSubsystem()
    quality = MLQualityControlSubsystem()

    orchestrator.register_subsystem("transport", transport)
    orchestrator.register_subsystem("quality", quality, dependencies=["transport"])

    # Initialize with configs
    configs = {
        "transport": SubsystemConfig({"enabled": True}),
        "quality": SubsystemConfig({"enabled": True})
    }
    orchestrator.initialize_all(configs)

    # Run a simple simulation
    context = SimulationContext(time=0, delta_time=0.1)

    print("\n📦 Running example simulation...")
    for i in range(10):
        # Simulate some events
        if i % 3 == 0:
            event = Event(
                type=EventType.TRANSPORT_REQUESTED,
                source="simulation",
                data={"from": "module_a", "to": "module_b"}
            )
            event_bus.publish(event)

        # Update all subsystems
        results = orchestrator.update_all(0.1, context)
        context.time += 0.1

        if i % 3 == 0:
            metrics = orchestrator.get_metrics()
            print(f"\nTime: {context.time:.1f}s")
            for name, m in metrics.items():
                if m:
                    print(f"  {name}: {m}")

    print("\n✅ Modular framework demonstration complete!")