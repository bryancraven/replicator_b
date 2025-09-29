#!/usr/bin/env python3
"""
Basic unit tests for modular_framework module
"""

import pytest
from collections import deque
from modular_framework import (
    EventType,
    Event,
    EventBus,
    SubsystemConfig,
    SimulationContext,
    SubsystemBase,
    MockSubsystem,
    UpdateStrategy,
    SubsystemOrchestrator,
    SubsystemRegistry,
)


class TestEventType:
    """Test EventType enum"""

    def test_event_types_exist(self):
        """Test that core event types are defined"""
        assert hasattr(EventType, 'RESOURCE_PRODUCED')
        assert hasattr(EventType, 'TASK_STARTED')
        assert hasattr(EventType, 'TASK_COMPLETED')
        assert hasattr(EventType, 'MODULE_CREATED')
        assert hasattr(EventType, 'ENERGY_AVAILABLE')

    def test_event_type_values(self):
        """Test event type string values"""
        assert EventType.RESOURCE_PRODUCED.value == "resource_produced"
        assert EventType.TASK_COMPLETED.value == "task_completed"


class TestEvent:
    """Test Event dataclass"""

    def test_event_creation(self):
        """Test creating an event"""
        event = Event(
            type=EventType.RESOURCE_PRODUCED,
            source="test_subsystem",
            data={"resource": "STEEL", "quantity": 100}
        )

        assert event.type == EventType.RESOURCE_PRODUCED
        assert event.source == "test_subsystem"
        assert event.data["resource"] == "STEEL"
        assert event.data["quantity"] == 100
        assert event.timestamp > 0

    def test_event_string_representation(self):
        """Test event __str__ method"""
        event = Event(
            type=EventType.TASK_STARTED,
            source="factory",
            data={}
        )

        event_str = str(event)
        assert "task_started" in event_str
        assert "factory" in event_str


class TestEventBus:
    """Test EventBus class"""

    def test_event_bus_creation(self):
        """Test creating an event bus"""
        bus = EventBus()
        assert bus.max_history == 1000
        assert isinstance(bus.event_history, deque)
        assert len(bus.event_history) == 0

    def test_event_bus_custom_history_size(self):
        """Test creating event bus with custom history size"""
        bus = EventBus(max_history=500)
        assert bus.max_history == 500
        assert bus.event_history.maxlen == 500

    def test_subscribe_and_publish(self):
        """Test subscribing to and publishing events"""
        bus = EventBus()
        received_events = []

        def handler(event: Event):
            received_events.append(event)

        bus.subscribe(EventType.RESOURCE_PRODUCED, handler)

        event = Event(
            type=EventType.RESOURCE_PRODUCED,
            source="test",
            data={"resource": "STEEL"}
        )
        bus.publish(event)
        bus.process_events()

        assert len(received_events) == 1
        assert received_events[0].type == EventType.RESOURCE_PRODUCED

    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event type"""
        bus = EventBus()
        calls = {"handler1": 0, "handler2": 0}

        def handler1(event: Event):
            calls["handler1"] += 1

        def handler2(event: Event):
            calls["handler2"] += 1

        bus.subscribe(EventType.TASK_COMPLETED, handler1)
        bus.subscribe(EventType.TASK_COMPLETED, handler2)

        event = Event(type=EventType.TASK_COMPLETED, source="test", data={})
        bus.publish(event)
        bus.process_events()

        assert calls["handler1"] == 1
        assert calls["handler2"] == 1

    def test_unsubscribe(self):
        """Test unsubscribing from events"""
        bus = EventBus()
        received = []

        def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.MODULE_CREATED, handler)
        bus.unsubscribe(EventType.MODULE_CREATED, handler)

        event = Event(type=EventType.MODULE_CREATED, source="test", data={})
        bus.publish(event)
        bus.process_events()

        assert len(received) == 0

    def test_event_history_bounded(self):
        """Test that event history is bounded by maxlen"""
        bus = EventBus(max_history=10)

        # Publish 20 events
        for i in range(20):
            event = Event(
                type=EventType.RESOURCE_PRODUCED,
                source="test",
                data={"index": i}
            )
            bus.publish(event)

        # Should only keep last 10
        assert len(bus.event_history) == 10
        # Check that oldest events were dropped
        assert bus.event_history[0].data["index"] == 10
        assert bus.event_history[-1].data["index"] == 19

    def test_get_history_unfiltered(self):
        """Test getting unfiltered event history"""
        bus = EventBus()

        for i in range(5):
            event = Event(
                type=EventType.RESOURCE_PRODUCED,
                source=f"source_{i}",
                data={}
            )
            bus.publish(event)

        history = bus.get_history()
        assert len(history) == 5

    def test_get_history_filtered_by_type(self):
        """Test filtering event history by type"""
        bus = EventBus()

        bus.publish(Event(type=EventType.RESOURCE_PRODUCED, source="a", data={}))
        bus.publish(Event(type=EventType.TASK_COMPLETED, source="b", data={}))
        bus.publish(Event(type=EventType.RESOURCE_PRODUCED, source="c", data={}))

        history = bus.get_history(event_type=EventType.RESOURCE_PRODUCED)
        assert len(history) == 2
        assert all(e.type == EventType.RESOURCE_PRODUCED for e in history)

    def test_get_history_filtered_by_source(self):
        """Test filtering event history by source"""
        bus = EventBus()

        bus.publish(Event(type=EventType.MODULE_CREATED, source="factory_a", data={}))
        bus.publish(Event(type=EventType.MODULE_CREATED, source="factory_b", data={}))
        bus.publish(Event(type=EventType.MODULE_CREATED, source="factory_a", data={}))

        history = bus.get_history(source="factory_a")
        assert len(history) == 2
        assert all(e.source == "factory_a" for e in history)


class TestSubsystemConfig:
    """Test SubsystemConfig class"""

    def test_config_creation_empty(self):
        """Test creating empty config"""
        config = SubsystemConfig()
        assert config.config == {}

    def test_config_creation_with_dict(self):
        """Test creating config with dictionary"""
        config = SubsystemConfig({"param1": 100, "param2": "value"})
        assert config.config["param1"] == 100
        assert config.config["param2"] == "value"

    def test_config_get_with_default(self):
        """Test getting config value with default"""
        config = SubsystemConfig({"existing": 42})

        assert config.get("existing") == 42
        assert config.get("missing") is None
        assert config.get("missing", "default") == "default"

    def test_config_merge(self):
        """Test merging configs"""
        config1 = SubsystemConfig({"a": 1, "b": 2})
        config2 = SubsystemConfig({"b": 3, "c": 4})

        config1.merge(config2)

        assert config1.config["a"] == 1
        assert config1.config["b"] == 3  # Overwritten
        assert config1.config["c"] == 4


class TestSimulationContext:
    """Test SimulationContext dataclass"""

    def test_context_creation(self):
        """Test creating a simulation context"""
        context = SimulationContext(
            time=100.0,
            delta_time=0.1,
            resources={"STEEL": 1000},
            modules={"cnc": {"count": 5}},
            tasks=[{"id": "task_001"}]
        )

        assert context.time == 100.0
        assert context.delta_time == 0.1
        assert context.resources["STEEL"] == 1000
        assert context.modules["cnc"]["count"] == 5
        assert len(context.tasks) == 1

    def test_context_copy(self):
        """Test copying a context"""
        original = SimulationContext(
            time=50.0,
            delta_time=0.5,
            resources={"IRON": 500},
            modules={},
            tasks=[]
        )

        copy = original.copy()

        assert copy.time == original.time
        assert copy.delta_time == original.delta_time
        assert copy.resources == original.resources
        # Verify it's a deep copy
        copy.resources["IRON"] = 1000
        assert original.resources["IRON"] == 500


class TestSubsystemBase:
    """Test SubsystemBase class"""

    def test_subsystem_creation(self):
        """Test creating a subsystem"""
        subsystem = SubsystemBase("test_subsystem")
        assert subsystem.name == "test_subsystem"
        assert subsystem.enabled is True
        assert subsystem.config is None
        assert subsystem.event_bus is None

    def test_subsystem_initialization(self):
        """Test initializing a subsystem"""
        subsystem = SubsystemBase("test")
        config = SubsystemConfig({"enabled": True, "param": 42})
        bus = EventBus()

        subsystem.initialize(config, bus)

        assert subsystem.config == config
        assert subsystem.event_bus == bus
        assert subsystem.enabled is True

    def test_subsystem_publish_event(self):
        """Test publishing events from subsystem"""
        subsystem = SubsystemBase("test")
        bus = EventBus()
        config = SubsystemConfig()
        subsystem.initialize(config, bus)

        received = []

        def handler(event: Event):
            received.append(event)

        bus.subscribe(EventType.RESOURCE_PRODUCED, handler)

        subsystem.publish_event(
            EventType.RESOURCE_PRODUCED,
            {"resource": "STEEL", "quantity": 100}
        )
        bus.process_events()

        assert len(received) == 1
        assert received[0].source == "test"

    def test_subsystem_get_metrics(self):
        """Test getting metrics from subsystem"""
        subsystem = SubsystemBase("test")
        subsystem.metrics = {"count": 42, "rate": 1.5}

        metrics = subsystem.get_metrics()

        assert metrics["count"] == 42
        assert metrics["rate"] == 1.5
        # Verify it's a copy
        metrics["count"] = 100
        assert subsystem.metrics["count"] == 42

    def test_subsystem_state_management(self):
        """Test get/set state"""
        subsystem = SubsystemBase("test")
        subsystem.state = {"value": 123}

        state = subsystem.get_state()
        assert state["value"] == 123

        subsystem.set_state({"value": 456})
        assert subsystem.state["value"] == 456


class TestMockSubsystem:
    """Test MockSubsystem for testing"""

    def test_mock_subsystem_creation(self):
        """Test creating a mock subsystem"""
        mock = MockSubsystem("mock", update_return={"result": "success"})
        assert mock.name == "mock"
        assert mock.update_count == 0

    def test_mock_subsystem_update(self):
        """Test mock subsystem update method"""
        mock = MockSubsystem("mock", update_return={"status": "ok"})
        config = SubsystemConfig()
        bus = EventBus()
        mock.initialize(config, bus)

        context = SimulationContext(time=0, delta_time=0.1)
        result = mock.update(0.1, context)

        assert result["status"] == "ok"
        assert mock.update_count == 1
        assert mock.metrics["update_count"] == 1

    def test_mock_subsystem_receives_events(self):
        """Test that mock subsystem records events"""
        mock = MockSubsystem("mock")
        config = SubsystemConfig()
        bus = EventBus()
        mock.initialize(config, bus)

        event = Event(type=EventType.MODULE_CREATED, source="test", data={})
        mock.handle_event(event)

        assert len(mock.events_received) == 1
        assert mock.events_received[0].type == EventType.MODULE_CREATED


class TestSubsystemOrchestrator:
    """Test SubsystemOrchestrator class"""

    def test_orchestrator_creation(self):
        """Test creating an orchestrator"""
        orchestrator = SubsystemOrchestrator()
        assert len(orchestrator.subsystems) == 0
        assert orchestrator.update_strategy == UpdateStrategy.SEQUENTIAL

    def test_register_subsystem(self):
        """Test registering a subsystem"""
        orchestrator = SubsystemOrchestrator()
        subsystem = MockSubsystem("test")

        orchestrator.register_subsystem("test", subsystem)

        assert "test" in orchestrator.subsystems
        assert orchestrator.subsystems["test"] == subsystem

    def test_register_subsystem_with_dependencies(self):
        """Test registering subsystem with dependencies"""
        orchestrator = SubsystemOrchestrator()
        sub1 = MockSubsystem("sub1")
        sub2 = MockSubsystem("sub2")

        orchestrator.register_subsystem("sub1", sub1)
        orchestrator.register_subsystem("sub2", sub2, dependencies=["sub1"])

        assert "sub2" in orchestrator.dependencies
        assert "sub1" in orchestrator.dependencies["sub2"]

    def test_update_order_respects_dependencies(self):
        """Test that update order respects dependencies"""
        orchestrator = SubsystemOrchestrator()

        sub1 = MockSubsystem("sub1")
        sub2 = MockSubsystem("sub2")
        sub3 = MockSubsystem("sub3")

        orchestrator.register_subsystem("sub1", sub1)
        orchestrator.register_subsystem("sub2", sub2, dependencies=["sub1"])
        orchestrator.register_subsystem("sub3", sub3, dependencies=["sub2"])

        # sub1 should come before sub2, sub2 before sub3
        assert orchestrator.update_order.index("sub1") < orchestrator.update_order.index("sub2")
        assert orchestrator.update_order.index("sub2") < orchestrator.update_order.index("sub3")


class TestSubsystemRegistry:
    """Test SubsystemRegistry class"""

    def test_registry_has_mock_subsystem(self):
        """Test that mock subsystem is registered"""
        available = SubsystemRegistry.list_available()
        assert "mock" in available

    def test_create_subsystem_from_registry(self):
        """Test creating subsystem from registry"""
        subsystem = SubsystemRegistry.create("mock", "test_instance")
        assert subsystem.name == "test_instance"
        assert isinstance(subsystem, MockSubsystem)

    def test_get_subsystem_class(self):
        """Test getting subsystem class from registry"""
        mock_class = SubsystemRegistry.get_class("mock")
        assert mock_class == MockSubsystem


if __name__ == "__main__":
    pytest.main([__file__, "-v"])