#!/usr/bin/env python3
"""
Example custom subsystems demonstrating the modular framework's extensibility

These subsystems show how to create specialized implementations for different
aspects of the factory simulation.
"""

from typing import Dict, Any, List
from collections import defaultdict, deque
import random
import math

from modular_framework import (
    SubsystemBase, SubsystemConfig, SimulationContext,
    Event, EventType, SubsystemRegistry
)


# ===============================================================================
# ADVANCED TRANSPORT SUBSYSTEMS
# ===============================================================================

class GeneticRoutingTransport(SubsystemBase):
    """Transport system using genetic algorithm for route optimization"""

    def __init__(self, name: str = "genetic_transport"):
        super().__init__(name)
        self.population_size = 50
        self.mutation_rate = 0.1
        self.generations_per_update = 5
        self.route_population = []
        self.best_routes = {}
        self.pending_transports = deque()
        self.active_transports = {}

    def initialize(self, config: SubsystemConfig, event_bus):
        """
        Initialize genetic routing transport system.

        Args:
            config: Subsystem configuration with optional parameters:
                - population_size (int): Size of route population for GA (default: 50)
                - mutation_rate (float): Probability of mutation (default: 0.1)
                - generations_per_update (int): GA generations per update (default: 5)
            event_bus: Event bus for inter-subsystem communication
        """
        super().initialize(config, event_bus)
        self.population_size = config.get("population_size", 50)
        self.mutation_rate = config.get("mutation_rate", 0.1)
        self.generations_per_update = config.get("generations_per_update", 5)

        # Subscribe to transport requests
        event_bus.subscribe(EventType.TRANSPORT_REQUESTED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        """
        Update transport system using genetic algorithm for route optimization.

        This method:
        1. Evolves route population using genetic algorithm
        2. Processes active transports (decrements time, completes finished)
        3. Starts new transports using optimized routes
        4. Publishes transport events

        Args:
            delta_time: Elapsed simulation time since last update (hours)
            context: Current simulation state (resources, modules, tasks)

        Returns:
            Dict containing:
                - completed (int): Number of transports completed this update
        """
        if not self.enabled:
            return {}

        # Evolve route population
        if self.pending_transports:
            self._evolve_routes()

        # Process active transports
        completed = []
        for transport_id, transport in list(self.active_transports.items()):
            transport["time_remaining"] -= delta_time
            if transport["time_remaining"] <= 0:
                completed.append(transport_id)
                self.publish_event(EventType.TRANSPORT_COMPLETED, {
                    "transport_id": transport_id,
                    "route": transport["route"]
                })
                del self.active_transports[transport_id]

        # Start new transports from optimized routes
        while self.pending_transports and len(self.active_transports) < 20:
            request = self.pending_transports.popleft()
            route = self._get_best_route(request["from"], request["to"])
            transport_id = f"gt_{self.time:.2f}_{random.randint(1000, 9999)}"

            self.active_transports[transport_id] = {
                "from": request["from"],
                "to": request["to"],
                "route": route,
                "time_remaining": self._calculate_route_time(route),
                "fitness": self._evaluate_route(route)
            }

            self.publish_event(EventType.TRANSPORT_STARTED, {
                "transport_id": transport_id,
                "estimated_time": self.active_transports[transport_id]["time_remaining"]
            })

        self.metrics["active_transports"] = len(self.active_transports)
        self.metrics["pending_transports"] = len(self.pending_transports)
        self.metrics["completed_this_update"] = len(completed)

        return {"completed": len(completed)}

    def _evolve_routes(self):
        """Evolve route population using genetic algorithm"""
        for _ in range(self.generations_per_update):
            # Selection
            parents = self._selection()

            # Crossover
            offspring = self._crossover(parents)

            # Mutation
            offspring = self._mutation(offspring)

            # Replace population
            self.route_population = self._replacement(self.route_population, offspring)

    def _selection(self) -> List[Dict]:
        """Tournament selection for breeding"""
        if not self.route_population:
            return []

        selected = []
        for _ in range(len(self.route_population) // 2):
            tournament = random.sample(
                self.route_population,
                min(3, len(self.route_population))
            )
            winner = max(tournament, key=lambda x: x.get("fitness", 0))
            selected.append(winner)
        return selected

    def _crossover(self, parents: List[Dict]) -> List[Dict]:
        """Create offspring through crossover"""
        offspring = []
        for i in range(0, len(parents) - 1, 2):
            parent1, parent2 = parents[i], parents[i + 1]
            # Simple crossover - mix route segments
            child = {
                "route": parent1.get("route", [])[:len(parent1.get("route", [])) // 2] +
                        parent2.get("route", [])[len(parent2.get("route", [])) // 2:],
                "fitness": 0
            }
            offspring.append(child)
        return offspring

    def _mutation(self, offspring: List[Dict]) -> List[Dict]:
        """Apply mutations to offspring"""
        for child in offspring:
            if random.random() < self.mutation_rate:
                route = child.get("route", [])
                if len(route) > 2:
                    # Swap two random positions
                    i, j = random.sample(range(len(route)), 2)
                    route[i], route[j] = route[j], route[i]
                    child["route"] = route
        return offspring

    def _replacement(self, population: List[Dict], offspring: List[Dict]) -> List[Dict]:
        """Replace population with best individuals"""
        combined = population + offspring
        for individual in combined:
            individual["fitness"] = self._evaluate_route(individual.get("route", []))

        # Keep best individuals
        combined.sort(key=lambda x: x.get("fitness", 0), reverse=True)
        return combined[:self.population_size]

    def _evaluate_route(self, route: List[str]) -> float:
        """Calculate fitness of a route"""
        if not route:
            return 0.0

        # Simple fitness: shorter routes are better
        base_fitness = 100.0 / (len(route) + 1)

        # Add bonus for direct routes
        if len(route) <= 2:
            base_fitness *= 1.5

        return base_fitness

    def _calculate_route_time(self, route: List[str]) -> float:
        """Calculate time for route traversal"""
        base_time = len(route) * 2.0  # 2 seconds per segment
        # Add congestion factor
        congestion = len(self.active_transports) / 20.0
        return base_time * (1 + congestion * 0.5)

    def _get_best_route(self, from_pos: str, to_pos: str) -> List[str]:
        """Get best evolved route or create default"""
        route_key = f"{from_pos}->{to_pos}"
        if route_key in self.best_routes:
            return self.best_routes[route_key]

        # Default direct route
        return [from_pos, to_pos]

    def handle_event(self, event: Event):
        """Handle transport requests"""
        if event.type == EventType.TRANSPORT_REQUESTED:
            self.pending_transports.append({
                "from": event.data.get("from", "storage"),
                "to": event.data.get("to", "assembly"),
                "priority": event.data.get("priority", 0)
            })


class SwarmTransportSystem(SubsystemBase):
    """Transport system using swarm intelligence for coordination"""

    def __init__(self, name: str = "swarm_transport"):
        super().__init__(name)
        self.swarm_size = 20
        self.agents = []
        self.pheromone_trails = defaultdict(float)
        self.evaporation_rate = 0.1

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)
        self.swarm_size = config.get("swarm_size", 20)
        self.evaporation_rate = config.get("evaporation_rate", 0.1)

        # Initialize swarm agents
        for i in range(self.swarm_size):
            self.agents.append({
                "id": f"agent_{i}",
                "position": "depot",
                "carrying": None,
                "target": None,
                "path": [],
                "status": "idle"
            })

        event_bus.subscribe(EventType.TRANSPORT_REQUESTED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Evaporate pheromone trails
        for trail in list(self.pheromone_trails.keys()):
            self.pheromone_trails[trail] *= (1 - self.evaporation_rate * delta_time)
            if self.pheromone_trails[trail] < 0.01:
                del self.pheromone_trails[trail]

        # Update each agent
        completed_transports = 0
        for agent in self.agents:
            if agent["status"] == "transporting" and agent["path"]:
                # Move along path
                agent["path"].pop(0)
                if not agent["path"]:
                    # Reached destination
                    self._deposit_pheromone(agent["position"], agent["target"])
                    agent["position"] = agent["target"]
                    agent["status"] = "idle"
                    agent["carrying"] = None
                    completed_transports += 1

                    self.publish_event(EventType.TRANSPORT_COMPLETED, {
                        "agent_id": agent["id"],
                        "delivered_to": agent["target"]
                    })

        self.metrics["active_agents"] = sum(1 for a in self.agents if a["status"] != "idle")
        self.metrics["completed_transports"] = completed_transports
        self.metrics["pheromone_trails"] = len(self.pheromone_trails)

        return {"completed": completed_transports}

    def _deposit_pheromone(self, from_pos: str, to_pos: str):
        """Deposit pheromone on successful path"""
        trail_key = f"{from_pos}->{to_pos}"
        self.pheromone_trails[trail_key] += 1.0

    def _find_best_path(self, from_pos: str, to_pos: str) -> List[str]:
        """Find path using pheromone trails"""
        trail_key = f"{from_pos}->{to_pos}"
        if self.pheromone_trails[trail_key] > 0.5:
            # Strong trail exists
            return [from_pos, to_pos]

        # Default path
        return [from_pos, "intermediate", to_pos]

    def handle_event(self, event: Event):
        """Assign transport to available agent"""
        if event.type == EventType.TRANSPORT_REQUESTED:
            # Find idle agent
            for agent in self.agents:
                if agent["status"] == "idle":
                    agent["status"] = "transporting"
                    agent["target"] = event.data.get("to", "assembly")
                    agent["carrying"] = event.data.get("resource", "material")
                    agent["path"] = self._find_best_path(
                        agent["position"],
                        agent["target"]
                    )

                    self.publish_event(EventType.TRANSPORT_STARTED, {
                        "agent_id": agent["id"],
                        "path_length": len(agent["path"])
                    })
                    break


# ===============================================================================
# ADVANCED QUALITY CONTROL SUBSYSTEMS
# ===============================================================================

class StatisticalProcessControl(SubsystemBase):
    """Statistical process control for quality monitoring"""

    def __init__(self, name: str = "spc_quality"):
        super().__init__(name)
        self.control_charts = defaultdict(lambda: {"values": deque(maxlen=50), "ucl": 0, "lcl": 0})
        self.capability_indices = {}
        self.out_of_control_signals = []

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)
        self.sigma_limit = config.get("sigma_limit", 3)
        self.min_samples = config.get("min_samples_for_limits", 20)

        event_bus.subscribe(EventType.TASK_COMPLETED, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Update control limits
        for metric_name, chart in self.control_charts.items():
            if len(chart["values"]) >= self.min_samples:
                values = list(chart["values"])
                mean = sum(values) / len(values)
                std = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))

                chart["ucl"] = mean + self.sigma_limit * std
                chart["lcl"] = mean - self.sigma_limit * std
                chart["mean"] = mean

                # Check for out-of-control signals
                if values[-1] > chart["ucl"] or values[-1] < chart["lcl"]:
                    self.out_of_control_signals.append({
                        "metric": metric_name,
                        "value": values[-1],
                        "ucl": chart["ucl"],
                        "lcl": chart["lcl"]
                    })

        # Calculate process capability
        self._calculate_capability_indices()

        self.metrics["monitored_metrics"] = len(self.control_charts)
        self.metrics["out_of_control_signals"] = len(self.out_of_control_signals)
        self.metrics["average_cpk"] = (
            sum(self.capability_indices.values()) / len(self.capability_indices)
            if self.capability_indices else 0
        )

        return {
            "signals": len(self.out_of_control_signals),
            "capability": self.metrics["average_cpk"]
        }

    def _calculate_capability_indices(self):
        """Calculate Cp and Cpk for processes"""
        for metric_name, chart in self.control_charts.items():
            if len(chart["values"]) >= self.min_samples and "mean" in chart:
                values = list(chart["values"])
                mean = chart["mean"]
                std = math.sqrt(sum((x - mean) ** 2 for x in values) / len(values))

                if std > 0:
                    # Assume spec limits are ±6 sigma from mean
                    usl = mean + 6 * std
                    lsl = mean - 6 * std

                    cp = (usl - lsl) / (6 * std)
                    cpu = (usl - mean) / (3 * std)
                    cpl = (mean - lsl) / (3 * std)
                    cpk = min(cpu, cpl)

                    self.capability_indices[metric_name] = cpk

    def handle_event(self, event: Event):
        """Track quality metrics from completed tasks"""
        if event.type == EventType.TASK_COMPLETED:
            # Track various quality metrics
            if "quality_score" in event.data:
                self.control_charts["quality_score"]["values"].append(
                    event.data["quality_score"]
                )
            if "cycle_time" in event.data:
                self.control_charts["cycle_time"]["values"].append(
                    event.data["cycle_time"]
                )
            if "defect_rate" in event.data:
                self.control_charts["defect_rate"]["values"].append(
                    event.data["defect_rate"]
                )


class PredictiveMaintenanceSystem(SubsystemBase):
    """Predictive maintenance using degradation modeling"""

    def __init__(self, name: str = "predictive_maintenance"):
        super().__init__(name)
        self.equipment_health = {}
        self.failure_predictions = {}
        self.maintenance_schedule = []
        self.degradation_models = {}

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)
        self.health_threshold = config.get("health_threshold", 0.3)
        self.prediction_horizon = config.get("prediction_horizon_hours", 168)

        event_bus.subscribe(EventType.MODULE_BUSY, self.handle_event)
        event_bus.subscribe(EventType.MODULE_IDLE, self.handle_event)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        maintenance_triggered = []

        # Update equipment health
        for module_id, health in list(self.equipment_health.items()):
            # Degradation based on usage
            if module_id in context.modules:
                module = context.modules[module_id]
                if module.get("status") == "active":
                    degradation_rate = self._get_degradation_rate(module_id, module)
                    self.equipment_health[module_id] -= degradation_rate * delta_time

                    # Predict failure time
                    if self.equipment_health[module_id] > 0:
                        time_to_failure = self.equipment_health[module_id] / degradation_rate
                        self.failure_predictions[module_id] = context.time + time_to_failure

                        # Schedule maintenance if needed
                        if time_to_failure < self.prediction_horizon:
                            self._schedule_maintenance(module_id, time_to_failure)

            # Trigger maintenance if health too low
            if self.equipment_health[module_id] < self.health_threshold:
                maintenance_triggered.append(module_id)
                self._perform_maintenance(module_id)

        self.metrics["monitored_equipment"] = len(self.equipment_health)
        self.metrics["scheduled_maintenance"] = len(self.maintenance_schedule)
        self.metrics["average_health"] = (
            sum(self.equipment_health.values()) / len(self.equipment_health)
            if self.equipment_health else 1.0
        )

        return {"maintenance_triggered": maintenance_triggered}

    def _get_degradation_rate(self, module_id: str, module: Dict) -> float:
        """Calculate degradation rate based on module usage"""
        base_rate = 0.001  # 0.1% per hour

        # Factors affecting degradation
        factors = 1.0

        # Temperature factor
        if "temperature" in module:
            temp = module["temperature"]
            if temp > 60:
                factors *= 1.5
            elif temp > 80:
                factors *= 2.0

        # Load factor
        if "load_factor" in module:
            load = module["load_factor"]
            factors *= (1 + load * 0.5)

        # Age factor
        if "age_hours" in module:
            age = module["age_hours"]
            factors *= (1 + age / 10000)  # Accelerating degradation

        return base_rate * factors

    def _schedule_maintenance(self, module_id: str, time_to_maintenance: float):
        """Schedule predictive maintenance"""
        # Check if already scheduled
        for scheduled in self.maintenance_schedule:
            if scheduled["module_id"] == module_id:
                return

        self.maintenance_schedule.append({
            "module_id": module_id,
            "scheduled_time": time_to_maintenance,
            "priority": 1 if time_to_maintenance < 24 else 0
        })

        self.publish_event(EventType.CUSTOM, {
            "type": "maintenance_scheduled",
            "module_id": module_id,
            "time_to_maintenance": time_to_maintenance
        })

    def _perform_maintenance(self, module_id: str):
        """Perform maintenance on module"""
        self.equipment_health[module_id] = 1.0  # Restore to full health
        self.failure_predictions.pop(module_id, None)

        # Remove from schedule
        self.maintenance_schedule = [
            s for s in self.maintenance_schedule
            if s["module_id"] != module_id
        ]

        self.publish_event(EventType.MODULE_REPAIRED, {
            "module_id": module_id,
            "health_restored": 1.0
        })

    def handle_event(self, event: Event):
        """Track module usage for health monitoring"""
        if event.type == EventType.MODULE_BUSY:
            module_id = event.data.get("module_id")
            if module_id and module_id not in self.equipment_health:
                self.equipment_health[module_id] = 1.0  # Start at full health


# ===============================================================================
# ADVANCED ENERGY SUBSYSTEMS
# ===============================================================================

class SmartGridEnergySystem(SubsystemBase):
    """Smart grid integration with demand response"""

    def __init__(self, name: str = "smart_grid"):
        super().__init__(name)
        self.grid_price_history = deque(maxlen=24)
        self.demand_forecast = []
        self.battery_strategy = "economic"
        self.grid_sales = 0
        self.grid_purchases = 0

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)
        self.grid_connected = config.get("grid_connection", False)
        self.max_grid_power = config.get("max_grid_power_kw", 1000)
        self.battery_capacity = config.get("battery_capacity_kwh", 500)
        self.battery_charge = self.battery_capacity * 0.5

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        hour_of_day = (context.time % 24)

        # Update grid price (time-of-use pricing)
        current_price = self._calculate_grid_price(hour_of_day)
        self.grid_price_history.append(current_price)

        # Forecast demand
        forecasted_demand = self._forecast_demand(context)
        self.demand_forecast = forecasted_demand

        # Make grid transaction decisions
        grid_transaction = 0
        if self.grid_connected:
            grid_transaction = self._optimize_grid_transaction(
                current_price,
                forecasted_demand,
                self.battery_charge
            )

            if grid_transaction > 0:
                # Buying from grid
                self.grid_purchases += grid_transaction * delta_time
                self.battery_charge += grid_transaction * delta_time
            elif grid_transaction < 0:
                # Selling to grid
                self.grid_sales += abs(grid_transaction) * delta_time
                self.battery_charge -= abs(grid_transaction) * delta_time

        # Ensure battery limits
        self.battery_charge = max(0, min(self.battery_capacity, self.battery_charge))

        self.metrics["battery_charge_kwh"] = self.battery_charge
        self.metrics["battery_percentage"] = self.battery_charge / self.battery_capacity
        self.metrics["current_grid_price"] = current_price
        self.metrics["grid_transaction_kw"] = grid_transaction
        self.metrics["total_grid_purchases_kwh"] = self.grid_purchases
        self.metrics["total_grid_sales_kwh"] = self.grid_sales

        return {
            "grid_transaction": grid_transaction,
            "battery_charge": self.battery_charge
        }

    def _calculate_grid_price(self, hour: float) -> float:
        """Calculate grid electricity price based on time of day"""
        # Peak hours: 16-21
        # Off-peak: 23-7
        # Mid-peak: other times

        if 16 <= hour <= 21:
            return 0.35  # $/kWh peak
        elif 23 <= hour or hour <= 7:
            return 0.10  # $/kWh off-peak
        else:
            return 0.20  # $/kWh mid-peak

    def _forecast_demand(self, context: SimulationContext) -> List[float]:
        """Forecast energy demand for next 24 hours"""
        forecast = []
        base_demand = 100  # kW

        for hour in range(24):
            # Simulate daily demand pattern
            demand = base_demand

            # Higher during work hours
            if 8 <= hour <= 17:
                demand *= 1.5

            # Account for active tasks
            active_tasks = len([t for t in context.tasks if t.get("status") == "active"])
            demand += active_tasks * 10

            forecast.append(demand)

        return forecast

    def _optimize_grid_transaction(self, price: float, forecast: List[float],
                                   battery: float) -> float:
        """Optimize grid buy/sell decision"""
        if self.battery_strategy == "economic":
            # Buy when cheap, sell when expensive
            avg_price = sum(self.grid_price_history) / len(self.grid_price_history) if self.grid_price_history else 0.20

            if price < avg_price * 0.8 and battery < self.battery_capacity * 0.8:
                # Buy power (charge battery)
                return min(self.max_grid_power, self.battery_capacity - battery)
            elif price > avg_price * 1.2 and battery > self.battery_capacity * 0.3:
                # Sell power
                return -min(self.max_grid_power * 0.5, battery - self.battery_capacity * 0.2)

        return 0


class RenewableEnergyOptimizer(SubsystemBase):
    """Optimizer for multiple renewable energy sources"""

    def __init__(self, name: str = "renewable_optimizer"):
        super().__init__(name)
        self.energy_sources = {}
        self.production_history = defaultdict(list)
        self.forecast_models = {}

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)

        # Initialize renewable sources
        self.energy_sources = {
            "solar": {
                "capacity_kw": config.get("solar_capacity_kw", 100),
                "efficiency": config.get("solar_efficiency", 0.22)
            },
            "wind": {
                "capacity_kw": config.get("wind_capacity_kw", 50),
                "efficiency": config.get("wind_efficiency", 0.40)
            },
            "geothermal": {
                "capacity_kw": config.get("geothermal_capacity_kw", 30),
                "efficiency": config.get("geothermal_efficiency", 0.85)
            }
        }

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        total_generation = 0
        generation_by_source = {}

        # Calculate generation from each source
        hour_of_day = (context.time % 24)
        day_of_year = int(context.time / 24) % 365

        # Solar generation
        if "solar" in self.energy_sources:
            solar = self.energy_sources["solar"]
            solar_generation = self._calculate_solar_generation(
                hour_of_day, day_of_year,
                solar["capacity_kw"], solar["efficiency"]
            )
            generation_by_source["solar"] = solar_generation
            total_generation += solar_generation

        # Wind generation
        if "wind" in self.energy_sources:
            wind = self.energy_sources["wind"]
            wind_generation = self._calculate_wind_generation(
                context.time, wind["capacity_kw"], wind["efficiency"]
            )
            generation_by_source["wind"] = wind_generation
            total_generation += wind_generation

        # Geothermal generation (constant)
        if "geothermal" in self.energy_sources:
            geo = self.energy_sources["geothermal"]
            geo_generation = geo["capacity_kw"] * geo["efficiency"]
            generation_by_source["geothermal"] = geo_generation
            total_generation += geo_generation

        # Store history for forecasting
        for source, generation in generation_by_source.items():
            self.production_history[source].append(generation)
            if len(self.production_history[source]) > 168:  # Keep 1 week
                self.production_history[source].pop(0)

        self.metrics["total_generation_kw"] = total_generation
        self.metrics["generation_by_source"] = generation_by_source
        self.metrics["renewable_percentage"] = 100.0  # All renewable

        # Publish energy availability
        self.publish_event(EventType.ENERGY_AVAILABLE, {
            "total_generation": total_generation,
            "sources": generation_by_source
        })

        return {"total_generation": total_generation}

    def _calculate_solar_generation(self, hour: float, day: int,
                                    capacity: float, efficiency: float) -> float:
        """Calculate solar generation based on time and season"""
        # Solar angle approximation
        solar_angle = math.sin(math.pi * (hour - 6) / 12) if 6 <= hour <= 18 else 0
        solar_angle = max(0, solar_angle)

        # Seasonal variation
        seasonal_factor = 0.8 + 0.4 * math.cos(2 * math.pi * day / 365)

        # Cloud cover (random variation)
        cloud_factor = 0.7 + random.random() * 0.3

        return capacity * efficiency * solar_angle * seasonal_factor * cloud_factor

    def _calculate_wind_generation(self, time: float, capacity: float,
                                   efficiency: float) -> float:
        """Calculate wind generation with variability"""
        # Simulate wind patterns
        base_wind = 0.5 + 0.3 * math.sin(time / 10)  # Slow variation
        gusts = 0.2 * math.sin(time * 3.7)  # Faster variation
        wind_factor = max(0, min(1, base_wind + gusts + random.random() * 0.1))

        return capacity * efficiency * wind_factor


# ===============================================================================
# DIGITAL TWIN SUBSYSTEM
# ===============================================================================

class DigitalTwinSubsystem(SubsystemBase):
    """Digital twin for predictive simulation and optimization"""

    def __init__(self, name: str = "digital_twin"):
        super().__init__(name)
        self.simulation_state = {}
        self.prediction_horizon = 100  # hours
        self.optimization_objectives = []
        self.scenario_results = {}

    def initialize(self, config: SubsystemConfig, event_bus):
        super().initialize(config, event_bus)
        self.prediction_horizon = config.get("prediction_horizon_hours", 100)
        self.update_frequency = config.get("update_frequency_hours", 10)
        self.scenarios_to_test = config.get("scenarios_to_test", 5)

    def update(self, delta_time: float, context: SimulationContext) -> Dict[str, Any]:
        if not self.enabled:
            return {}

        # Periodically run predictive simulations
        if int(context.time) % self.update_frequency == 0:
            self._run_predictive_simulations(context)

        # Analyze results and make recommendations
        recommendations = self._generate_recommendations()

        self.metrics["scenarios_tested"] = len(self.scenario_results)
        self.metrics["best_scenario"] = self._find_best_scenario()
        self.metrics["predicted_bottlenecks"] = self._predict_bottlenecks()

        return {"recommendations": recommendations}

    def _run_predictive_simulations(self, context: SimulationContext):
        """Run what-if scenarios in digital twin"""
        self.scenario_results = {}

        for i in range(self.scenarios_to_test):
            scenario_name = f"scenario_{i}"

            # Create scenario variations
            scenario_context = context.copy()

            # Vary parameters
            if i == 0:
                # Baseline
                pass
            elif i == 1:
                # Increase production rate
                scenario_context.tasks = context.tasks * 2
            elif i == 2:
                # Add more modules
                scenario_context.modules = {**context.modules, "extra_module": {}}
            elif i == 3:
                # Reduce resources
                for resource in scenario_context.resources:
                    scenario_context.resources[resource] *= 0.5
            elif i == 4:
                # Optimize scheduling
                scenario_context.tasks = sorted(
                    context.tasks,
                    key=lambda x: x.get("priority", 0),
                    reverse=True
                )

            # Run simplified simulation
            result = self._simulate_scenario(scenario_context)
            self.scenario_results[scenario_name] = result

    def _simulate_scenario(self, context: SimulationContext) -> Dict:
        """Run simplified simulation of scenario"""
        # Simplified simulation logic
        completion_time = len(context.tasks) * 10  # Simple estimate
        resource_utilization = sum(context.resources.values()) / 1000
        bottlenecks = []

        if resource_utilization > 0.8:
            bottlenecks.append("resources")
        if len(context.tasks) > 100:
            bottlenecks.append("processing_capacity")

        return {
            "completion_time": completion_time,
            "resource_utilization": resource_utilization,
            "bottlenecks": bottlenecks,
            "efficiency": 1.0 / (completion_time * (1 + len(bottlenecks)))
        }

    def _find_best_scenario(self) -> str:
        """Find scenario with best efficiency"""
        if not self.scenario_results:
            return "none"

        return max(
            self.scenario_results.items(),
            key=lambda x: x[1].get("efficiency", 0)
        )[0]

    def _predict_bottlenecks(self) -> List[str]:
        """Predict future bottlenecks"""
        bottlenecks = set()
        for result in self.scenario_results.values():
            bottlenecks.update(result.get("bottlenecks", []))
        return list(bottlenecks)

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []

        best = self._find_best_scenario()
        if best and best != "scenario_0":
            if best == "scenario_1":
                recommendations.append("Increase production rate for better efficiency")
            elif best == "scenario_2":
                recommendations.append("Add more processing modules")
            elif best == "scenario_3":
                recommendations.append("Current resource levels are excessive")
            elif best == "scenario_4":
                recommendations.append("Optimize task scheduling by priority")

        bottlenecks = self._predict_bottlenecks()
        for bottleneck in bottlenecks:
            recommendations.append(f"Address predicted bottleneck: {bottleneck}")

        return recommendations


# ===============================================================================
# REGISTRATION
# ===============================================================================

# Register all custom subsystems
SubsystemRegistry.register("genetic_routing", GeneticRoutingTransport)
SubsystemRegistry.register("swarm_transport", SwarmTransportSystem)
SubsystemRegistry.register("spc_quality", StatisticalProcessControl)
SubsystemRegistry.register("predictive_maintenance", PredictiveMaintenanceSystem)
SubsystemRegistry.register("smart_grid", SmartGridEnergySystem)
SubsystemRegistry.register("renewable_optimizer", RenewableEnergyOptimizer)
SubsystemRegistry.register("digital_twin", DigitalTwinSubsystem)


if __name__ == "__main__":
    print("Custom Subsystems for Modular Factory")
    print("=" * 60)

    # List all registered custom subsystems
    custom_subsystems = [
        "genetic_routing", "swarm_transport", "spc_quality",
        "predictive_maintenance", "smart_grid", "renewable_optimizer",
        "digital_twin"
    ]

    print("\nRegistered Custom Subsystems:")
    for name in custom_subsystems:
        subsystem_class = SubsystemRegistry.get_class(name)
        if subsystem_class:
            print(f"  ✓ {name}: {subsystem_class.__doc__.strip()}")

    print("\n✅ All custom subsystems registered successfully!")