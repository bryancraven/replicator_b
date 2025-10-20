#!/usr/bin/env python3
"""
Ultra-Realistic Self-Replicating Solar Factory Simulation
Complete with chemical processing, transport systems, software production,
precision manufacturing, waste management, and comprehensive material physics
"""

import heapq
import json
import math
import random
import sys
import argparse
import os
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum
from collections import defaultdict, deque

# ===============================================================================
# CONFIGURATION
# ===============================================================================

CONFIG = {
    # Energy parameters
    "initial_solar_capacity_kw": 100,
    "solar_panel_efficiency": 0.22,
    "battery_efficiency": 0.95,

    # Processing multipliers
    "mining_power_multiplier": 1.0,
    "processing_speed_multiplier": 1.0,
    "assembly_speed_multiplier": 1.0,
    "parallel_processing_limit": 10,

    # Maintenance
    "maintenance_interval_hours": 500,
    "learning_curve_factor": 0.95,
    "redundancy_factor": 1.2,

    # Ultra-realistic features - all enabled
    "enable_capacity_limits": True,
    "enable_degradation": True,
    "enable_quality_control": True,
    "enable_weather": True,
    "enable_maintenance": True,
    "enable_storage_limits": True,
    "enable_batch_processing": True,
    "enable_transport_time": True,
    "enable_contamination": True,
    "enable_thermal_management": True,
    "enable_software_production": True,
    "enable_waste_recycling": True,

    # Physical constraints
    "factory_area_m2": 20000,
    "max_storage_volume_m3": 15000,
    "max_storage_weight_tons": 10000,

    # Environmental
    "latitude": 35.0,  # degrees
    "average_cloud_cover": 0.3,
    "ambient_temperature": 25,  # Celsius

    # Quality targets
    "target_quality_rate": 0.95,
    "cleanroom_class": 1000,  # Class 1000 clean room

    # Transport
    "agv_fleet_size": 10,
    "conveyor_length_m": 500,
}

# ===============================================================================
# SIMULATION CONSTANTS
# ===============================================================================

# Task processing limits
MAX_TASK_STARTS_PER_STEP = 5
MAX_LOG_ENTRIES = 5000
LOG_TRIM_SIZE = 2500

# Transport constants
TRANSPORT_POWER_KW_PER_ACTIVE = 2.0
MAX_CONCURRENT_TRANSPORTS = 20
TRANSPORT_PRIORITY_OFFSET = 50

# Maintenance and cleaning
WEEKLY_CLEANING_INTERVAL_HOURS = 168

# Metric collection
METRIC_COLLECTION_INTERVAL_HOURS = 1.0
PROGRESS_REPORT_INTERVAL_HOURS = 100.0

# Event queue
EVENT_QUEUE_DROP_LOG_INTERVAL = 100

# Default wall-clock timeout
DEFAULT_WALL_CLOCK_TIMEOUT_SECONDS = 3600

# ===============================================================================
# RESOURCE TYPES - ULTRA COMPREHENSIVE
# ===============================================================================

class ResourceType(Enum):
    # Raw materials (directly mined)
    SILICON_ORE = "silicon_ore"
    IRON_ORE = "iron_ore"
    COPPER_ORE = "copper_ore"
    ALUMINUM_ORE = "aluminum_ore"
    LITHIUM_ORE = "lithium_ore"
    RARE_EARTH_ORE = "rare_earth_ore"
    CARBON_ORE = "carbon_ore"  # For plastics/carbon fiber

    # Chemical products
    SULFURIC_ACID = "sulfuric_acid"
    HYDROCHLORIC_ACID = "hydrochloric_acid"
    SODIUM_HYDROXIDE = "sodium_hydroxide"
    ORGANIC_SOLVENT = "organic_solvent"
    ELECTROLYTE_SOLUTION = "electrolyte_solution"
    POLYMER_RESIN = "polymer_resin"
    EPOXY = "epoxy"
    SILICONE = "silicone"
    LUBRICANT = "lubricant"
    COOLANT = "coolant"

    # Refined materials
    PURE_SILICON = "pure_silicon"
    STEEL = "steel"
    COPPER_WIRE = "copper_wire"
    ALUMINUM_SHEET = "aluminum_sheet"
    LITHIUM_COMPOUND = "lithium_compound"
    RARE_EARTH_MAGNETS = "rare_earth_magnets"
    GLASS = "glass"
    PLASTIC = "plastic"
    CARBON_FIBER = "carbon_fiber"
    CERAMIC = "ceramic"

    # Precision mechanical components
    BEARING = "bearing"
    PRECISION_BEARING = "precision_bearing"
    GEAR = "gear"
    BALL_SCREW = "ball_screw"
    LINEAR_GUIDE = "linear_guide"
    SPRING = "spring"
    DAMPER = "damper"
    COUPLING = "coupling"

    # Fasteners and seals
    BOLT = "bolt"
    SCREW = "screw"
    WASHER = "washer"
    ORING = "oring"
    GASKET = "gasket"

    # Electronic basics
    SILICON_WAFER = "silicon_wafer"
    TRANSISTOR = "transistor"
    CAPACITOR = "capacitor"
    RESISTOR = "resistor"
    INDUCTOR = "inductor"
    DIODE = "diode"
    LED = "led"

    # Electronic advanced
    INTEGRATED_CIRCUIT = "integrated_circuit"
    MICROPROCESSOR = "microprocessor"
    MEMORY_CHIP = "memory_chip"
    POWER_REGULATOR = "power_regulator"
    VOLTAGE_REGULATOR = "voltage_regulator"
    CRYSTAL_OSCILLATOR = "crystal_oscillator"

    # Sensors
    THERMOCOUPLE = "thermocouple"
    PRESSURE_TRANSDUCER = "pressure_transducer"
    FLOW_METER = "flow_meter"
    PROXIMITY_SENSOR = "proximity_sensor"
    ENCODER = "encoder"
    LOAD_CELL = "load_cell"
    CAMERA_MODULE = "camera_module"
    LIDAR = "lidar"
    STRAIN_GAUGE = "strain_gauge"  # Added missing sensor

    # Actuators and motors
    MOTOR_COIL = "motor_coil"
    ELECTRIC_MOTOR = "electric_motor"
    SERVO_MOTOR = "servo_motor"
    STEPPER_MOTOR = "stepper_motor"
    LINEAR_ACTUATOR = "linear_actuator"
    PNEUMATIC_CYLINDER = "pneumatic_cylinder"
    SOLENOID_VALVE = "solenoid_valve"

    # PCB and connections
    PCB_SUBSTRATE = "pcb_substrate"
    SOLDER_PASTE = "solder_paste"
    CONNECTOR = "connector"
    WIRE_HARNESS = "wire_harness"
    LEAD = "lead"  # Solder materials
    TIN = "tin"
    FLUX = "flux"

    # Power components
    BATTERY_CELL = "battery_cell"
    SOLAR_CELL = "solar_cell"
    TRANSFORMER = "transformer"
    INVERTER = "inverter"

    # Thermal management
    HEAT_SINK = "heat_sink"
    HEAT_EXCHANGER = "heat_exchanger"
    COOLING_FAN = "cooling_fan"
    RADIATOR = "radiator"
    CHILLER_UNIT = "chiller_unit"

    # Chemical processing equipment
    REACTION_VESSEL = "reaction_vessel"
    DISTILLATION_COLUMN = "distillation_column"
    CATALYST = "catalyst"
    SEPARATION_MEMBRANE = "separation_membrane"
    CHEMICAL_PUMP = "chemical_pump"

    # Precision manufacturing
    CNC_SPINDLE = "cnc_spindle"
    LASER_DIODE = "laser_diode"
    FOCUSING_LENS = "focusing_lens"
    VACUUM_PUMP = "vacuum_pump"
    MASS_FLOW_CONTROLLER = "mass_flow_controller"
    COMPRESSOR = "compressor"  # Added for pneumatics/cooling

    # Testing equipment
    OSCILLOSCOPE = "oscilloscope"
    MULTIMETER = "multimeter"
    TENSILE_TESTER = "tensile_tester"
    CMM_PROBE = "cmm_probe"
    DISPLAY_PANEL = "display_panel"  # Added for display

    # Clean room equipment
    HEPA_FILTER = "hepa_filter"
    LAMINAR_FLOW_HOOD = "laminar_flow_hood"
    PARTICLE_COUNTER = "particle_counter"

    # Transport equipment
    CONVEYOR_BELT = "conveyor_belt"
    CONVEYOR_MOTOR = "conveyor_motor"
    AGV_CHASSIS = "agv_chassis"
    AGV_NAVIGATION = "agv_navigation"

    # Software/firmware
    PLC_PROGRAM = "plc_program"
    ROBOT_FIRMWARE = "robot_firmware"
    AI_MODEL = "ai_model"
    SCADA_SYSTEM = "scada_system"

    # Recycling equipment
    SHREDDER = "shredder"
    MAGNETIC_SEPARATOR = "magnetic_separator"
    OPTICAL_SORTER = "optical_sorter"

    # Advanced assemblies
    CONTROL_BOARD = "control_board"
    ROBOTIC_ARM = "robotic_arm"
    CONVEYOR_SYSTEM = "conveyor_system"
    PRINTER_HEAD_3D = "3d_printer_head"
    FURNACE_ELEMENT = "furnace_element"
    SOLAR_PANEL = "solar_panel"
    BATTERY_PACK = "battery_pack"

    # Factory modules
    MINING_MODULE = "mining_module"
    REFINING_MODULE = "refining_module"
    CHEMICAL_MODULE = "chemical_module"
    ELECTRONICS_MODULE = "electronics_module"
    MECHANICAL_MODULE = "mechanical_module"
    CNC_MODULE = "cnc_module"
    LASER_MODULE = "laser_module"
    ASSEMBLY_MODULE = "assembly_module"
    SOFTWARE_MODULE = "software_module"
    TRANSPORT_MODULE = "transport_module"
    RECYCLING_MODULE = "recycling_module"
    TESTING_MODULE = "testing_module"
    CLEANROOM_MODULE = "cleanroom_module"
    THERMAL_MODULE = "thermal_module"
    POWER_MODULE = "power_module"
    CONTROL_MODULE = "control_module"

# ===============================================================================
# RECIPES - ULTRA COMPREHENSIVE
# ===============================================================================

@dataclass
class Recipe:
    """Defines how to produce a resource/component"""
    output: ResourceType
    output_quantity: int
    inputs: Dict[ResourceType, int]
    energy_kwh: float
    time_hours: float
    required_module: Optional[str] = None
    parallel_capable: bool = True
    tolerance_um: Optional[float] = None  # Precision requirement
    cleanroom_class: Optional[int] = None  # Contamination requirement
    software_required: Optional[ResourceType] = None  # Software dependency
    waste_products: Optional[Dict[ResourceType, float]] = None  # Waste generation

# Define all recipes (production chains)
RECIPES = [
    # Raw material extraction (per ton)
    Recipe(ResourceType.SILICON_ORE, 1000, {}, 50, 1.0, "mining"),
    Recipe(ResourceType.IRON_ORE, 1000, {}, 40, 0.8, "mining"),
    Recipe(ResourceType.COPPER_ORE, 1000, {}, 60, 1.2, "mining"),
    Recipe(ResourceType.ALUMINUM_ORE, 1000, {}, 70, 1.5, "mining"),
    Recipe(ResourceType.LITHIUM_ORE, 100, {}, 100, 3.0, "mining"),
    Recipe(ResourceType.RARE_EARTH_ORE, 10, {}, 200, 5.0, "mining"),
    Recipe(ResourceType.CARBON_ORE, 500, {}, 30, 0.5, "mining"),

    # Chemical products
    Recipe(ResourceType.SULFURIC_ACID, 100, {ResourceType.CARBON_ORE: 50}, 80, 2.0, "chemical"),  # Using carbon ore as base
    Recipe(ResourceType.POLYMER_RESIN, 50, {ResourceType.CARBON_ORE: 100, ResourceType.CATALYST: 1}, 120, 3.0, "chemical"),
    Recipe(ResourceType.ELECTROLYTE_SOLUTION, 100, {ResourceType.LITHIUM_COMPOUND: 20, ResourceType.ORGANIC_SOLVENT: 50}, 60, 1.5, "chemical"),
    Recipe(ResourceType.EPOXY, 20, {ResourceType.POLYMER_RESIN: 10, ResourceType.CATALYST: 0.5}, 40, 1.0, "chemical"),
    Recipe(ResourceType.LUBRICANT, 100, {ResourceType.CARBON_ORE: 50}, 30, 0.8, "chemical"),
    Recipe(ResourceType.COOLANT, 200, {ResourceType.ORGANIC_SOLVENT: 100}, 20, 0.5, "chemical"),

    # Refined materials
    Recipe(ResourceType.PURE_SILICON, 100, {ResourceType.SILICON_ORE: 500}, 200, 2.0, "refining"),
    Recipe(ResourceType.STEEL, 500, {ResourceType.IRON_ORE: 600, ResourceType.CARBON_ORE: 10}, 150, 1.5, "refining"),
    Recipe(ResourceType.COPPER_WIRE, 200, {ResourceType.COPPER_ORE: 250}, 80, 1.0, "refining"),
    Recipe(ResourceType.ALUMINUM_SHEET, 300, {ResourceType.ALUMINUM_ORE: 400}, 100, 1.2, "refining"),
    Recipe(ResourceType.LITHIUM_COMPOUND, 50, {ResourceType.LITHIUM_ORE: 80}, 120, 2.0, "refining"),
    Recipe(ResourceType.RARE_EARTH_MAGNETS, 5, {ResourceType.RARE_EARTH_ORE: 8}, 150, 3.0, "refining"),
    Recipe(ResourceType.GLASS, 100, {ResourceType.SILICON_ORE: 150}, 80, 0.8, "refining"),
    Recipe(ResourceType.PLASTIC, 100, {ResourceType.POLYMER_RESIN: 80}, 60, 0.5, "refining"),
    Recipe(ResourceType.CARBON_FIBER, 10, {ResourceType.CARBON_ORE: 50, ResourceType.POLYMER_RESIN: 5}, 200, 4.0, "refining"),

    # Precision mechanical components (CNC required)
    Recipe(ResourceType.PRECISION_BEARING, 10, {ResourceType.STEEL: 5, ResourceType.LUBRICANT: 0.1}, 40, 1.0, "cnc", tolerance_um=5),
    Recipe(ResourceType.BALL_SCREW, 5, {ResourceType.STEEL: 10, ResourceType.LUBRICANT: 0.2}, 60, 2.0, "cnc", tolerance_um=10),
    Recipe(ResourceType.LINEAR_GUIDE, 5, {ResourceType.STEEL: 15, ResourceType.LUBRICANT: 0.3}, 80, 2.5, "cnc", tolerance_um=10),

    # Electronic components (cleanroom required)
    Recipe(ResourceType.SILICON_WAFER, 100, {ResourceType.PURE_SILICON: 10}, 50, 0.5, "cleanroom", cleanroom_class=100),
    Recipe(ResourceType.TRANSISTOR, 10000, {ResourceType.SILICON_WAFER: 1}, 20, 0.2, "cleanroom", cleanroom_class=10),
    Recipe(ResourceType.INTEGRATED_CIRCUIT, 100, {
        ResourceType.SILICON_WAFER: 1,
        ResourceType.TRANSISTOR: 1000,
        ResourceType.CAPACITOR: 100,
        ResourceType.RESISTOR: 200
    }, 100, 1.0, "cleanroom", cleanroom_class=10),

    # Software/firmware production
    Recipe(ResourceType.PLC_PROGRAM, 1, {}, 0.5, 40.0, "software", software_required=None),
    Recipe(ResourceType.ROBOT_FIRMWARE, 1, {}, 1.0, 80.0, "software", software_required=ResourceType.PLC_PROGRAM),
    Recipe(ResourceType.AI_MODEL, 1, {}, 5.0, 200.0, "software", software_required=ResourceType.ROBOT_FIRMWARE),
    Recipe(ResourceType.SCADA_SYSTEM, 1, {}, 2.0, 120.0, "software", software_required=ResourceType.PLC_PROGRAM),

    # Transport equipment
    Recipe(ResourceType.AGV_CHASSIS, 1, {
        ResourceType.STEEL: 200,
        ResourceType.PLASTIC: 50,
        ResourceType.BEARING: 20
    }, 300, 5.0, "assembly"),
    Recipe(ResourceType.AGV_NAVIGATION, 1, {
        ResourceType.LIDAR: 2,
        ResourceType.CAMERA_MODULE: 4,
        ResourceType.CONTROL_BOARD: 1,
        ResourceType.AI_MODEL: 1
    }, 100, 3.0, "assembly"),
    Recipe(ResourceType.CONVEYOR_BELT, 10, {
        ResourceType.PLASTIC: 100,
        ResourceType.STEEL: 20
    }, 50, 1.0, "assembly"),
    Recipe(ResourceType.CONVEYOR_MOTOR, 1, {
        ResourceType.ELECTRIC_MOTOR: 1,
        ResourceType.GEAR: 5,
        ResourceType.BEARING: 4
    }, 40, 0.5, "assembly"),

    # Chemical processing equipment
    Recipe(ResourceType.REACTION_VESSEL, 1, {
        ResourceType.STEEL: 500,
        ResourceType.GLASS: 50,
        ResourceType.GASKET: 10,
        ResourceType.PRESSURE_TRANSDUCER: 2
    }, 400, 8.0, "assembly"),
    Recipe(ResourceType.DISTILLATION_COLUMN, 1, {
        ResourceType.STEEL: 800,
        ResourceType.HEAT_EXCHANGER: 5,
        ResourceType.THERMOCOUPLE: 10,
        ResourceType.CONTROL_BOARD: 1
    }, 600, 12.0, "assembly"),

    # Testing equipment
    Recipe(ResourceType.CMM_PROBE, 1, {
        ResourceType.PRECISION_BEARING: 6,
        ResourceType.LINEAR_ACTUATOR: 3,
        ResourceType.ENCODER: 3,
        ResourceType.CONTROL_BOARD: 1
    }, 200, 4.0, "assembly", tolerance_um=0.1),

    # Recycling equipment
    Recipe(ResourceType.SHREDDER, 1, {
        ResourceType.STEEL: 300,
        ResourceType.ELECTRIC_MOTOR: 5,
        ResourceType.GEAR: 20
    }, 500, 6.0, "assembly"),
    Recipe(ResourceType.MAGNETIC_SEPARATOR, 1, {
        ResourceType.RARE_EARTH_MAGNETS: 50,
        ResourceType.STEEL: 100,
        ResourceType.CONVEYOR_BELT: 5
    }, 300, 4.0, "assembly"),

    # Advanced components
    Recipe(ResourceType.SOLAR_CELL, 100, {
        ResourceType.SILICON_WAFER: 10,
        ResourceType.GLASS: 10,
        ResourceType.ALUMINUM_SHEET: 2,
        ResourceType.COPPER_WIRE: 5
    }, 120, 1.2, "cleanroom", cleanroom_class=1000),

    Recipe(ResourceType.SOLAR_PANEL, 10, {
        ResourceType.SOLAR_CELL: 60,
        ResourceType.GLASS: 50,
        ResourceType.ALUMINUM_SHEET: 20,
        ResourceType.PLASTIC: 30,
        ResourceType.CONNECTOR: 10
    }, 200, 2.0, "assembly"),

    Recipe(ResourceType.BATTERY_PACK, 10, {
        ResourceType.BATTERY_CELL: 100,
        ResourceType.CONTROL_BOARD: 1,
        ResourceType.PLASTIC: 50,
        ResourceType.COPPER_WIRE: 20,
        ResourceType.COOLANT: 5
    }, 250, 2.5, "assembly"),

    Recipe(ResourceType.CONTROL_BOARD, 20, {
        ResourceType.MICROPROCESSOR: 2,
        ResourceType.MEMORY_CHIP: 8,
        ResourceType.POWER_REGULATOR: 4,
        ResourceType.INTEGRATED_CIRCUIT: 10,
        ResourceType.CAPACITOR: 200,
        ResourceType.RESISTOR: 500,
        ResourceType.PCB_SUBSTRATE: 1,
        ResourceType.SOLDER_PASTE: 0.5
    }, 150, 1.5, "cleanroom", cleanroom_class=10000),

    Recipe(ResourceType.ROBOTIC_ARM, 5, {
        ResourceType.SERVO_MOTOR: 6,
        ResourceType.LINEAR_ACTUATOR: 3,
        ResourceType.ENCODER: 6,
        ResourceType.CONTROL_BOARD: 2,
        ResourceType.STEEL: 100,
        ResourceType.ALUMINUM_SHEET: 50,
        ResourceType.WIRE_HARNESS: 2,
        ResourceType.ROBOT_FIRMWARE: 1
    }, 500, 5.0, "assembly"),

    # Factory modules (the big pieces) with software requirements
    Recipe(ResourceType.MINING_MODULE, 1, {
        ResourceType.ROBOTIC_ARM: 4,
        ResourceType.CONVEYOR_SYSTEM: 2,
        ResourceType.CONTROL_BOARD: 10,
        ResourceType.STEEL: 2000,
        ResourceType.ELECTRIC_MOTOR: 20,
        ResourceType.PLC_PROGRAM: 1
    }, 2000, 20.0, "assembly"),

    Recipe(ResourceType.CHEMICAL_MODULE, 1, {
        ResourceType.REACTION_VESSEL: 3,
        ResourceType.DISTILLATION_COLUMN: 2,
        ResourceType.CHEMICAL_PUMP: 10,
        ResourceType.CONTROL_BOARD: 15,
        ResourceType.STEEL: 2500,
        ResourceType.SCADA_SYSTEM: 1
    }, 3000, 30.0, "assembly"),

    Recipe(ResourceType.CNC_MODULE, 1, {
        ResourceType.CNC_SPINDLE: 3,
        ResourceType.LINEAR_GUIDE: 9,
        ResourceType.BALL_SCREW: 9,
        ResourceType.SERVO_MOTOR: 12,
        ResourceType.CONTROL_BOARD: 5,
        ResourceType.STEEL: 1500,
        ResourceType.ROBOT_FIRMWARE: 1
    }, 2500, 25.0, "assembly"),

    Recipe(ResourceType.CLEANROOM_MODULE, 1, {
        ResourceType.HEPA_FILTER: 20,
        ResourceType.LAMINAR_FLOW_HOOD: 5,
        ResourceType.PARTICLE_COUNTER: 10,
        ResourceType.CONTROL_BOARD: 10,
        ResourceType.STEEL: 3000,
        ResourceType.GLASS: 500,
        ResourceType.SCADA_SYSTEM: 1
    }, 4000, 40.0, "assembly"),

    Recipe(ResourceType.SOFTWARE_MODULE, 1, {
        ResourceType.MICROPROCESSOR: 100,
        ResourceType.MEMORY_CHIP: 500,
        ResourceType.CONTROL_BOARD: 50,
        ResourceType.COOLING_FAN: 20,
        ResourceType.STEEL: 500,
        ResourceType.AI_MODEL: 1
    }, 2000, 20.0, "assembly"),

    Recipe(ResourceType.TRANSPORT_MODULE, 1, {
        ResourceType.AGV_CHASSIS: 10,
        ResourceType.AGV_NAVIGATION: 10,
        ResourceType.CONVEYOR_MOTOR: 20,
        ResourceType.CONVEYOR_BELT: 50,
        ResourceType.CONTROL_BOARD: 20,
        ResourceType.AI_MODEL: 1
    }, 3500, 35.0, "assembly"),

    Recipe(ResourceType.RECYCLING_MODULE, 1, {
        ResourceType.SHREDDER: 2,
        ResourceType.MAGNETIC_SEPARATOR: 3,
        ResourceType.OPTICAL_SORTER: 2,
        ResourceType.CONVEYOR_SYSTEM: 3,
        ResourceType.CONTROL_BOARD: 10,
        ResourceType.STEEL: 2000,
        ResourceType.PLC_PROGRAM: 1
    }, 2800, 28.0, "assembly"),

    Recipe(ResourceType.TESTING_MODULE, 1, {
        ResourceType.CMM_PROBE: 2,
        ResourceType.OSCILLOSCOPE: 5,
        ResourceType.TENSILE_TESTER: 2,
        ResourceType.CONTROL_BOARD: 20,
        ResourceType.STEEL: 1500,
        ResourceType.SCADA_SYSTEM: 1
    }, 3000, 30.0, "assembly"),

    Recipe(ResourceType.THERMAL_MODULE, 1, {
        ResourceType.CHILLER_UNIT: 2,
        ResourceType.HEAT_EXCHANGER: 10,
        ResourceType.RADIATOR: 5,
        ResourceType.COOLING_FAN: 20,
        ResourceType.THERMOCOUPLE: 50,
        ResourceType.CONTROL_BOARD: 10,
        ResourceType.STEEL: 1500,
        ResourceType.COOLANT: 500,
        ResourceType.PLC_PROGRAM: 1
    }, 2500, 25.0, "assembly"),

    Recipe(ResourceType.POWER_MODULE, 1, {
        ResourceType.SOLAR_PANEL: 100,
        ResourceType.BATTERY_PACK: 50,
        ResourceType.INVERTER: 20,
        ResourceType.TRANSFORMER: 10,
        ResourceType.CONTROL_BOARD: 20,
        ResourceType.COPPER_WIRE: 2000,
        ResourceType.SCADA_SYSTEM: 1
    }, 4000, 40.0, "assembly"),

    Recipe(ResourceType.CONTROL_MODULE, 1, {
        ResourceType.MICROPROCESSOR: 50,
        ResourceType.MEMORY_CHIP: 200,
        ResourceType.CONTROL_BOARD: 50,
        ResourceType.PROXIMITY_SENSOR: 100,
        ResourceType.ENCODER: 50,
        ResourceType.COPPER_WIRE: 2000,
        ResourceType.AI_MODEL: 1,
        ResourceType.SCADA_SYSTEM: 1
    }, 3000, 30.0, "assembly"),
]

# Add missing component recipes
additional_recipes = [
    # Basic mechanical
    Recipe(ResourceType.BEARING, 100, {ResourceType.STEEL: 5}, 30, 0.3, "mechanical"),
    Recipe(ResourceType.GEAR, 50, {ResourceType.STEEL: 10}, 40, 0.4, "mechanical"),
    Recipe(ResourceType.SPRING, 200, {ResourceType.STEEL: 2}, 10, 0.1, "mechanical"),
    Recipe(ResourceType.COUPLING, 50, {ResourceType.STEEL: 5}, 20, 0.2, "mechanical"),

    # Fasteners
    Recipe(ResourceType.BOLT, 1000, {ResourceType.STEEL: 5}, 10, 0.1, "mechanical"),
    Recipe(ResourceType.SCREW, 1000, {ResourceType.STEEL: 3}, 8, 0.08, "mechanical"),
    Recipe(ResourceType.WASHER, 2000, {ResourceType.STEEL: 2}, 5, 0.05, "mechanical"),

    # Seals
    Recipe(ResourceType.ORING, 500, {ResourceType.PLASTIC: 2}, 10, 0.1, "mechanical"),
    Recipe(ResourceType.GASKET, 200, {ResourceType.PLASTIC: 5}, 15, 0.15, "mechanical"),

    # Basic electronics
    Recipe(ResourceType.CAPACITOR, 1000, {ResourceType.ALUMINUM_SHEET: 1, ResourceType.PLASTIC: 2}, 10, 0.1, "electronics"),
    Recipe(ResourceType.RESISTOR, 1000, {ResourceType.COPPER_WIRE: 1, ResourceType.CERAMIC: 0.5}, 5, 0.05, "electronics"),
    Recipe(ResourceType.INDUCTOR, 500, {ResourceType.COPPER_WIRE: 5, ResourceType.STEEL: 1}, 20, 0.2, "electronics"),
    Recipe(ResourceType.DIODE, 1000, {ResourceType.SILICON_WAFER: 0.5}, 15, 0.15, "electronics"),
    Recipe(ResourceType.LED, 500, {ResourceType.SILICON_WAFER: 1, ResourceType.PLASTIC: 1}, 15, 0.15, "electronics"),

    # Motors
    Recipe(ResourceType.ELECTRIC_MOTOR, 20, {
        ResourceType.MOTOR_COIL: 4,
        ResourceType.RARE_EARTH_MAGNETS: 2,
        ResourceType.BEARING: 4,
        ResourceType.STEEL: 20
    }, 100, 1.0, "mechanical"),
    Recipe(ResourceType.SERVO_MOTOR, 10, {
        ResourceType.ELECTRIC_MOTOR: 1,
        ResourceType.ENCODER: 1,
        ResourceType.CONTROL_BOARD: 0.2,
        ResourceType.GEAR: 5
    }, 150, 1.5, "assembly"),
    Recipe(ResourceType.STEPPER_MOTOR, 20, {
        ResourceType.MOTOR_COIL: 8,
        ResourceType.RARE_EARTH_MAGNETS: 4,
        ResourceType.BEARING: 2,
        ResourceType.STEEL: 10
    }, 120, 1.2, "mechanical"),

    # Actuators
    Recipe(ResourceType.LINEAR_ACTUATOR, 10, {
        ResourceType.ELECTRIC_MOTOR: 1,
        ResourceType.BALL_SCREW: 1,
        ResourceType.LINEAR_GUIDE: 2,
        ResourceType.ENCODER: 1
    }, 200, 2.0, "assembly"),
    Recipe(ResourceType.PNEUMATIC_CYLINDER, 20, {
        ResourceType.ALUMINUM_SHEET: 10,
        ResourceType.ORING: 4,
        ResourceType.STEEL: 5
    }, 80, 0.8, "mechanical"),
    Recipe(ResourceType.SOLENOID_VALVE, 50, {
        ResourceType.STEEL: 2,
        ResourceType.COPPER_WIRE: 5,
        ResourceType.ORING: 2
    }, 40, 0.4, "mechanical"),

    # More sensors
    Recipe(ResourceType.THERMOCOUPLE, 100, {ResourceType.COPPER_WIRE: 2, ResourceType.STEEL: 0.5}, 20, 0.2, "electronics"),
    Recipe(ResourceType.PRESSURE_TRANSDUCER, 50, {
        ResourceType.SILICON_WAFER: 0.5,
        ResourceType.STEEL: 2,
        ResourceType.INTEGRATED_CIRCUIT: 0.5
    }, 60, 0.6, "electronics"),
    Recipe(ResourceType.FLOW_METER, 20, {
        ResourceType.STEEL: 5,
        ResourceType.PRESSURE_TRANSDUCER: 1,  # Using pressure transducer instead of generic sensor
        ResourceType.INTEGRATED_CIRCUIT: 1
    }, 100, 1.0, "assembly"),
    Recipe(ResourceType.PROXIMITY_SENSOR, 100, {
        ResourceType.LED: 1,
        ResourceType.INTEGRATED_CIRCUIT: 0.5,
        ResourceType.PLASTIC: 2
    }, 30, 0.3, "electronics"),
    Recipe(ResourceType.ENCODER, 50, {
        ResourceType.LED: 2,
        ResourceType.INTEGRATED_CIRCUIT: 1,
        ResourceType.GLASS: 1
    }, 80, 0.8, "electronics"),
    Recipe(ResourceType.LOAD_CELL, 20, {
        ResourceType.STEEL: 5,
        ResourceType.STRAIN_GAUGE: 4,
        ResourceType.INTEGRATED_CIRCUIT: 1
    }, 120, 1.2, "assembly"),
    Recipe(ResourceType.CAMERA_MODULE, 10, {
        ResourceType.INTEGRATED_CIRCUIT: 5,
        ResourceType.GLASS: 2,
        ResourceType.PLASTIC: 5
    }, 150, 1.5, "electronics"),
    Recipe(ResourceType.LIDAR, 5, {
        ResourceType.LASER_DIODE: 1,
        ResourceType.INTEGRATED_CIRCUIT: 10,
        ResourceType.GLASS: 5,
        ResourceType.SERVO_MOTOR: 1
    }, 300, 3.0, "assembly"),

    # Power electronics
    Recipe(ResourceType.VOLTAGE_REGULATOR, 100, {
        ResourceType.INTEGRATED_CIRCUIT: 1,
        ResourceType.CAPACITOR: 10,
        ResourceType.INDUCTOR: 2
    }, 40, 0.4, "electronics"),
    Recipe(ResourceType.CRYSTAL_OSCILLATOR, 200, {
        ResourceType.SILICON_WAFER: 0.2,
        ResourceType.STEEL: 0.5
    }, 30, 0.3, "electronics"),
    Recipe(ResourceType.TRANSFORMER, 20, {
        ResourceType.COPPER_WIRE: 100,
        ResourceType.STEEL: 50
    }, 150, 1.5, "mechanical"),
    Recipe(ResourceType.INVERTER, 10, {
        ResourceType.POWER_REGULATOR: 4,
        ResourceType.CAPACITOR: 50,
        ResourceType.HEAT_SINK: 2,
        ResourceType.CONTROL_BOARD: 1
    }, 200, 2.0, "assembly"),

    # Thermal components
    Recipe(ResourceType.HEAT_SINK, 100, {ResourceType.ALUMINUM_SHEET: 5}, 30, 0.3, "mechanical"),
    Recipe(ResourceType.HEAT_EXCHANGER, 10, {
        ResourceType.ALUMINUM_SHEET: 50,
        ResourceType.COPPER_WIRE: 20,
        ResourceType.STEEL: 20
    }, 200, 2.0, "mechanical"),
    Recipe(ResourceType.COOLING_FAN, 50, {
        ResourceType.PLASTIC: 5,
        ResourceType.ELECTRIC_MOTOR: 0.5,
        ResourceType.BEARING: 2
    }, 40, 0.4, "assembly"),
    Recipe(ResourceType.RADIATOR, 10, {
        ResourceType.ALUMINUM_SHEET: 30,
        ResourceType.COPPER_WIRE: 10,
        ResourceType.COOLING_FAN: 2
    }, 150, 1.5, "assembly"),
    Recipe(ResourceType.CHILLER_UNIT, 2, {
        ResourceType.HEAT_EXCHANGER: 2,
        ResourceType.COMPRESSOR: 1,
        ResourceType.CONTROL_BOARD: 2,
        ResourceType.STEEL: 200
    }, 500, 5.0, "assembly"),

    # More chemical equipment
    Recipe(ResourceType.CHEMICAL_PUMP, 20, {
        ResourceType.STEEL: 20,
        ResourceType.ELECTRIC_MOTOR: 1,
        ResourceType.GASKET: 5,
        ResourceType.COUPLING: 2
    }, 150, 1.5, "assembly"),
    Recipe(ResourceType.CATALYST, 10, {ResourceType.RARE_EARTH_ORE: 5}, 100, 2.0, "chemical"),
    Recipe(ResourceType.SEPARATION_MEMBRANE, 20, {
        ResourceType.POLYMER_RESIN: 10,
        ResourceType.CERAMIC: 5
    }, 150, 3.0, "chemical"),

    # CNC components
    Recipe(ResourceType.CNC_SPINDLE, 5, {
        ResourceType.STEEL: 50,
        ResourceType.PRECISION_BEARING: 10,
        ResourceType.SERVO_MOTOR: 1
    }, 300, 3.0, "assembly"),
    Recipe(ResourceType.LASER_DIODE, 50, {
        ResourceType.SILICON_WAFER: 2,
        ResourceType.RARE_EARTH_MAGNETS: 0.5
    }, 100, 1.0, "cleanroom", cleanroom_class=1000),
    Recipe(ResourceType.FOCUSING_LENS, 100, {ResourceType.GLASS: 5}, 50, 0.5, "mechanical", tolerance_um=1),
    Recipe(ResourceType.VACUUM_PUMP, 5, {
        ResourceType.STEEL: 100,
        ResourceType.ELECTRIC_MOTOR: 2,
        ResourceType.GASKET: 10
    }, 400, 4.0, "assembly"),
    Recipe(ResourceType.MASS_FLOW_CONTROLLER, 20, {
        ResourceType.FLOW_METER: 1,
        ResourceType.SOLENOID_VALVE: 2,
        ResourceType.CONTROL_BOARD: 0.5
    }, 200, 2.0, "assembly"),

    # Test equipment
    Recipe(ResourceType.OSCILLOSCOPE, 5, {
        ResourceType.CONTROL_BOARD: 5,
        ResourceType.DISPLAY_PANEL: 1,
        ResourceType.PLASTIC: 20
    }, 500, 5.0, "assembly"),
    Recipe(ResourceType.MULTIMETER, 50, {
        ResourceType.INTEGRATED_CIRCUIT: 2,
        ResourceType.DISPLAY_PANEL: 0.2,
        ResourceType.PLASTIC: 2
    }, 50, 0.5, "assembly"),
    Recipe(ResourceType.TENSILE_TESTER, 2, {
        ResourceType.LOAD_CELL: 2,
        ResourceType.LINEAR_ACTUATOR: 2,
        ResourceType.STEEL: 200,
        ResourceType.CONTROL_BOARD: 2
    }, 600, 6.0, "assembly"),

    # Clean room equipment
    Recipe(ResourceType.HEPA_FILTER, 50, {
        ResourceType.POLYMER_RESIN: 10,
        ResourceType.ALUMINUM_SHEET: 5
    }, 100, 1.0, "assembly"),
    Recipe(ResourceType.LAMINAR_FLOW_HOOD, 5, {
        ResourceType.HEPA_FILTER: 4,
        ResourceType.COOLING_FAN: 4,
        ResourceType.STEEL: 100,
        ResourceType.GLASS: 20
    }, 400, 4.0, "assembly"),
    Recipe(ResourceType.PARTICLE_COUNTER, 10, {
        ResourceType.LASER_DIODE: 1,
        ResourceType.INTEGRATED_CIRCUIT: 5,
        ResourceType.PLASTIC: 10
    }, 200, 2.0, "assembly"),

    # PCB components
    Recipe(ResourceType.PCB_SUBSTRATE, 100, {
        ResourceType.GLASS: 10,
        ResourceType.POLYMER_RESIN: 5,
        ResourceType.COPPER_WIRE: 2
    }, 100, 1.0, "electronics"),
    Recipe(ResourceType.SOLDER_PASTE, 10, {
        ResourceType.LEAD: 5,
        ResourceType.TIN: 5,
        ResourceType.FLUX: 1
    }, 50, 0.5, "chemical"),
    Recipe(ResourceType.CONNECTOR, 500, {
        ResourceType.PLASTIC: 5,
        ResourceType.COPPER_WIRE: 2
    }, 30, 0.3, "mechanical"),
    Recipe(ResourceType.WIRE_HARNESS, 20, {
        ResourceType.COPPER_WIRE: 50,
        ResourceType.CONNECTOR: 20,
        ResourceType.PLASTIC: 10
    }, 100, 1.0, "assembly"),

    # Recycling components
    Recipe(ResourceType.OPTICAL_SORTER, 2, {
        ResourceType.CAMERA_MODULE: 10,
        ResourceType.CONVEYOR_BELT: 5,
        ResourceType.CONTROL_BOARD: 5,
        ResourceType.AI_MODEL: 1
    }, 600, 6.0, "assembly"),
]

# Add additional recipes to main list
RECIPES.extend(additional_recipes)

# Add some missing basic materials that were referenced but not defined
missing_basics = [
    Recipe(ResourceType.CERAMIC, 100, {ResourceType.SILICON_ORE: 50, ResourceType.ALUMINUM_ORE: 20}, 200, 2.0, "refining"),
    Recipe(ResourceType.ORGANIC_SOLVENT, 100, {ResourceType.CARBON_ORE: 50}, 80, 1.0, "chemical"),
    Recipe(ResourceType.MOTOR_COIL, 20, {ResourceType.COPPER_WIRE: 50, ResourceType.STEEL: 5}, 25, 0.5, "mechanical"),
    # Additional missing materials
    Recipe(ResourceType.LEAD, 100, {ResourceType.CARBON_ORE: 20}, 50, 0.5, "refining"),  # Simplified
    Recipe(ResourceType.TIN, 100, {ResourceType.ALUMINUM_ORE: 20}, 50, 0.5, "refining"),  # Simplified
    Recipe(ResourceType.FLUX, 50, {ResourceType.ORGANIC_SOLVENT: 10}, 30, 0.3, "chemical"),
    Recipe(ResourceType.STRAIN_GAUGE, 100, {ResourceType.RESISTOR: 10, ResourceType.STEEL: 1}, 40, 0.4, "electronics"),
    Recipe(ResourceType.COMPRESSOR, 5, {ResourceType.ELECTRIC_MOTOR: 1, ResourceType.STEEL: 50}, 200, 2.0, "mechanical"),
    Recipe(ResourceType.DISPLAY_PANEL, 10, {ResourceType.GLASS: 20, ResourceType.LED: 100, ResourceType.INTEGRATED_CIRCUIT: 5}, 300, 3.0, "assembly"),
]

RECIPES.extend(missing_basics)

# ===============================================================================
# Continue with rest of the simulation code...
# ===============================================================================

# The file is getting very long, so I'll continue in the next part...
# ===============================================================================
# MODULE SPECIFICATIONS - ULTRA REALISTIC
# ===============================================================================

@dataclass
class ModuleSpec:
    """Ultra-realistic specifications for each module type"""
    module_type: str
    max_throughput: float  # units/hour
    power_consumption_idle: float  # kW
    power_consumption_active: float  # kW
    mtbf_hours: float  # Mean time between failures
    maintenance_interval: float  # hours
    degradation_rate: float  # % per 1000 hours
    physical_footprint: float  # m²
    max_batch_size: float  # units
    min_batch_size: float  # units
    setup_time: float  # hours for changeover
    quality_base_rate: float  # Base quality rate (0-1)
    tolerance_capability: Optional[float] = None  # Precision in micrometers
    cleanroom_capable: Optional[int] = None  # Clean room class capability

MODULE_SPECS = {
    "mining": ModuleSpec(
        module_type="mining",
        max_throughput=10.0,
        power_consumption_idle=5.0,
        power_consumption_active=50.0,
        mtbf_hours=5000,
        maintenance_interval=500,
        degradation_rate=0.02,
        physical_footprint=500,
        max_batch_size=100,
        min_batch_size=1,
        setup_time=0.5,
        quality_base_rate=0.98
    ),
    "refining": ModuleSpec(
        module_type="refining",
        max_throughput=5.0,
        power_consumption_idle=10.0,
        power_consumption_active=100.0,
        mtbf_hours=4000,
        maintenance_interval=300,
        degradation_rate=0.03,
        physical_footprint=300,
        max_batch_size=50,
        min_batch_size=5,
        setup_time=2.0,
        quality_base_rate=0.95
    ),
    "chemical": ModuleSpec(
        module_type="chemical",
        max_throughput=2.0,
        power_consumption_idle=20.0,
        power_consumption_active=200.0,
        mtbf_hours=3000,
        maintenance_interval=400,
        degradation_rate=0.04,
        physical_footprint=250,
        max_batch_size=500,
        min_batch_size=50,
        setup_time=4.0,
        quality_base_rate=0.92
    ),
    "electronics": ModuleSpec(
        module_type="electronics",
        max_throughput=1000.0,
        power_consumption_idle=20.0,
        power_consumption_active=80.0,
        mtbf_hours=3000,
        maintenance_interval=200,
        degradation_rate=0.04,
        physical_footprint=200,
        max_batch_size=10000,
        min_batch_size=100,
        setup_time=3.0,
        quality_base_rate=0.90
    ),
    "mechanical": ModuleSpec(
        module_type="mechanical",
        max_throughput=100.0,
        power_consumption_idle=15.0,
        power_consumption_active=60.0,
        mtbf_hours=4500,
        maintenance_interval=400,
        degradation_rate=0.025,
        physical_footprint=400,
        max_batch_size=500,
        min_batch_size=10,
        setup_time=1.5,
        quality_base_rate=0.97
    ),
    "cnc": ModuleSpec(
        module_type="cnc",
        max_throughput=20.0,
        power_consumption_idle=10.0,
        power_consumption_active=50.0,
        mtbf_hours=3000,
        maintenance_interval=100,
        degradation_rate=0.05,
        physical_footprint=100,
        max_batch_size=50,
        min_batch_size=1,
        setup_time=1.0,
        quality_base_rate=0.98,
        tolerance_capability=5.0
    ),
    "laser": ModuleSpec(
        module_type="laser",
        max_throughput=50.0,
        power_consumption_idle=5.0,
        power_consumption_active=100.0,
        mtbf_hours=2000,
        maintenance_interval=200,
        degradation_rate=0.06,
        physical_footprint=80,
        max_batch_size=100,
        min_batch_size=1,
        setup_time=0.5,
        quality_base_rate=0.99,
        tolerance_capability=1.0
    ),
    "cleanroom": ModuleSpec(
        module_type="cleanroom",
        max_throughput=100.0,
        power_consumption_idle=50.0,
        power_consumption_active=150.0,
        mtbf_hours=5000,
        maintenance_interval=100,
        degradation_rate=0.02,
        physical_footprint=300,
        max_batch_size=1000,
        min_batch_size=10,
        setup_time=6.0,
        quality_base_rate=0.95,
        cleanroom_capable=10
    ),
    "assembly": ModuleSpec(
        module_type="assembly",
        max_throughput=50.0,
        power_consumption_idle=10.0,
        power_consumption_active=40.0,
        mtbf_hours=6000,
        maintenance_interval=600,
        degradation_rate=0.015,
        physical_footprint=600,
        max_batch_size=200,
        min_batch_size=1,
        setup_time=1.0,
        quality_base_rate=0.96
    ),
    "software": ModuleSpec(
        module_type="software",
        max_throughput=1000.0,  # lines of code/hour
        power_consumption_idle=1.0,
        power_consumption_active=5.0,
        mtbf_hours=50000,
        maintenance_interval=2000,
        degradation_rate=0.001,
        physical_footprint=50,
        max_batch_size=1000000,
        min_batch_size=100,
        setup_time=1.0,
        quality_base_rate=0.90  # 10% bug rate
    ),
    "transport": ModuleSpec(
        module_type="transport",
        max_throughput=2000.0,  # kg/hour
        power_consumption_idle=2.0,
        power_consumption_active=20.0,
        mtbf_hours=8000,
        maintenance_interval=1000,
        degradation_rate=0.01,
        physical_footprint=1000,
        max_batch_size=2000,
        min_batch_size=1,
        setup_time=0.1,
        quality_base_rate=0.999
    ),
    "recycling": ModuleSpec(
        module_type="recycling",
        max_throughput=5.0,
        power_consumption_idle=10.0,
        power_consumption_active=100.0,
        mtbf_hours=4000,
        maintenance_interval=500,
        degradation_rate=0.03,
        physical_footprint=400,
        max_batch_size=1000,
        min_batch_size=100,
        setup_time=2.0,
        quality_base_rate=0.85
    ),
    "testing": ModuleSpec(
        module_type="testing",
        max_throughput=100.0,
        power_consumption_idle=5.0,
        power_consumption_active=30.0,
        mtbf_hours=10000,
        maintenance_interval=1000,
        degradation_rate=0.01,
        physical_footprint=200,
        max_batch_size=100,
        min_batch_size=1,
        setup_time=0.5,
        quality_base_rate=0.999,
        tolerance_capability=0.1
    ),
    "thermal": ModuleSpec(
        module_type="thermal",
        max_throughput=10000.0,  # kW of cooling
        power_consumption_idle=50.0,
        power_consumption_active=500.0,
        mtbf_hours=6000,
        maintenance_interval=500,
        degradation_rate=0.02,
        physical_footprint=300,
        max_batch_size=10000,
        min_batch_size=100,
        setup_time=0.0,
        quality_base_rate=1.0
    ),
}

# ===============================================================================
# TRANSPORT SYSTEM
# ===============================================================================

@dataclass
class TransportJob:
    """A material transport job"""
    job_id: str
    from_module: str
    to_module: str
    resource_type: ResourceType
    quantity: float
    priority: int
    distance: float
    assigned_vehicle: Optional[str] = None
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    energy_consumed: float = 0.0

class TransportSystem:
    """Ultra-realistic material transport and logistics"""

    def __init__(self, config):
        self.config = config
        self.transport_queue = []
        self.active_transports: Dict[str, TransportJob] = {}
        self.completed_transports = []

        # AGV fleet
        self.agv_fleet = {}
        for i in range(config.get("agv_fleet_size", 10)):
            agv_id = f"agv_{i:03d}"
            self.agv_fleet[agv_id] = {
                "status": "idle",
                "battery_level": 1.0,
                "current_load": 0,
                "max_load": 2000,  # kg
                "speed_mps": 1.0,
                "location": "depot",
                "maintenance_hours": 0
            }

        # Conveyor system
        self.conveyor_capacity = 1000  # kg
        self.conveyor_speed = 2.0  # m/s
        self.conveyor_utilization = 0.0

        # Layout distances (simplified grid)
        self.module_locations = self._generate_layout()

    def _generate_layout(self):
        """Generate factory layout with module positions"""
        locations = {}
        modules = ["mining", "refining", "chemical", "electronics", "mechanical",
                  "cnc", "laser", "cleanroom", "assembly", "software",
                  "transport", "recycling", "testing", "thermal"]

        # Arrange in a grid
        grid_size = math.ceil(math.sqrt(len(modules)))
        for i, module in enumerate(modules):
            x = (i % grid_size) * 50  # 50m spacing
            y = (i // grid_size) * 50
            locations[module] = (x, y)

        return locations

    def calculate_distance(self, from_module: str, to_module: str) -> float:
        """Calculate distance between modules"""
        if from_module not in self.module_locations or to_module not in self.module_locations:
            return 100  # Default distance

        x1, y1 = self.module_locations[from_module]
        x2, y2 = self.module_locations[to_module]

        # Manhattan distance (following paths)
        return abs(x2 - x1) + abs(y2 - y1)

    def schedule_transport(self, from_module: str, to_module: str,
                          resource: ResourceType, quantity: float,
                          priority: int = 100) -> Optional[TransportJob]:
        """Schedule a transport job"""
        job_id = f"transport_{len(self.transport_queue):06d}"

        distance = self.calculate_distance(from_module, to_module)

        job = TransportJob(
            job_id=job_id,
            from_module=from_module,
            to_module=to_module,
            resource_type=resource,
            quantity=quantity,
            priority=priority,
            distance=distance
        )

        heapq.heappush(self.transport_queue, (priority, job_id, job))
        return job

    def find_available_agv(self, load_weight: float) -> Optional[str]:
        """Find an available AGV with sufficient capacity"""
        for agv_id, agv in self.agv_fleet.items():
            if (agv["status"] == "idle" and
                agv["battery_level"] > 0.2 and
                agv["max_load"] >= load_weight):
                return agv_id
        return None

    def process_transport_queue(self, current_time: float):
        """Process pending transport jobs"""
        jobs_started = 0
        max_starts = 5

        while self.transport_queue and jobs_started < max_starts:
            priority, job_id, job = heapq.heappop(self.transport_queue)

            # Check if we can use conveyor for small items
            if job.quantity < 100 and self.conveyor_utilization < 0.8:
                # Use conveyor
                travel_time = job.distance / self.conveyor_speed / 3600  # hours
                job.completion_time = current_time + travel_time
                job.energy_consumed = job.distance * 0.5  # kWh
                self.conveyor_utilization += job.quantity / self.conveyor_capacity
                self.active_transports[job_id] = job
                jobs_started += 1

            else:
                # Try to find AGV
                agv_id = self.find_available_agv(job.quantity)
                if agv_id:
                    agv = self.agv_fleet[agv_id]
                    
                    # Calculate transport time
                    load_time = job.quantity / 1000 * 0.1  # hours
                    travel_time = job.distance / agv["speed_mps"] / 3600
                    unload_time = load_time

                    total_time = load_time + travel_time + unload_time
                    
                    # Update AGV status
                    agv["status"] = "transporting"
                    agv["current_load"] = job.quantity
                    agv["battery_level"] -= job.distance * 0.001  # Battery consumption

                    job.assigned_vehicle = agv_id
                    job.start_time = current_time
                    job.completion_time = current_time + total_time
                    job.energy_consumed = job.distance * 2.0  # kWh

                    self.active_transports[job_id] = job
                    jobs_started += 1

                else:
                    # No AGV available, put back in queue
                    heapq.heappush(self.transport_queue, (priority, job_id, job))
                    break

    def update_active_transports(self, current_time: float):
        """Update active transport jobs"""
        completed = []

        for job_id, job in self.active_transports.items():
            if current_time >= job.completion_time:
                # Job completed
                if job.assigned_vehicle:
                    agv = self.agv_fleet[job.assigned_vehicle]
                    agv["status"] = "idle"
                    agv["current_load"] = 0
                    agv["location"] = job.to_module
                    agv["maintenance_hours"] += job.completion_time - job.start_time

                self.completed_transports.append(job)
                completed.append(job_id)

                # Update conveyor utilization
                if job.quantity < 100:
                    self.conveyor_utilization = max(0, self.conveyor_utilization - job.quantity / self.conveyor_capacity)

        for job_id in completed:
            del self.active_transports[job_id]

    def maintain_agvs(self, current_time: float):
        """Perform AGV maintenance and charging"""
        for agv_id, agv in self.agv_fleet.items():
            # Charge if battery low and idle
            if agv["status"] == "idle" and agv["battery_level"] < 0.3:
                agv["status"] = "charging"

            # Charging
            if agv["status"] == "charging":
                agv["battery_level"] = min(1.0, agv["battery_level"] + 0.1)  # 10% per hour
                if agv["battery_level"] >= 0.95:
                    agv["status"] = "idle"

            # Scheduled maintenance
            if agv["maintenance_hours"] > 100:
                agv["status"] = "maintenance"
                agv["maintenance_hours"] = 0

# ===============================================================================
# WASTE MANAGEMENT SYSTEM
# ===============================================================================

class WasteStream:
    """Track and manage waste products"""

    def __init__(self):
        self.waste_inventory = defaultdict(float)
        self.recyclable_materials = {
            ResourceType.STEEL: 0.95,
            ResourceType.ALUMINUM_SHEET: 0.90,
            ResourceType.COPPER_WIRE: 0.85,
            ResourceType.PLASTIC: 0.60,
            ResourceType.GLASS: 0.80,
            ResourceType.SILICON_WAFER: 0.70,
        }

    def add_waste(self, waste_type: ResourceType, quantity: float):
        """Add waste to stream"""
        self.waste_inventory[waste_type] += quantity

    def process_recycling(self, waste_type: ResourceType, quantity: float) -> float:
        """Process waste for recycling"""
        if waste_type not in self.recyclable_materials:
            return 0.0

        available = min(quantity, self.waste_inventory.get(waste_type, 0))
        recovery_rate = self.recyclable_materials[waste_type]

        recovered = available * recovery_rate
        self.waste_inventory[waste_type] -= available

        return recovered

    def get_total_waste(self) -> float:
        """Get total waste volume"""
        return sum(self.waste_inventory.values())

# ===============================================================================
# CONTAMINATION TRACKING
# ===============================================================================

class CleanRoomEnvironment:
    """Track and manage cleanroom contamination"""

    def __init__(self, cleanroom_class: int):
        self.cleanroom_class = cleanroom_class
        self.particle_count = self._get_base_particles(cleanroom_class)
        self.time_since_cleaning = 0

    def _get_base_particles(self, cleanroom_class: int) -> float:
        """Get base particle count for cleanroom class"""
        # Particles per cubic meter at 0.5 micron
        class_standards = {
            1: 35.2,
            10: 352,
            100: 3520,
            1000: 35200,
            10000: 352000,
            100000: 3520000
        }
        return class_standards.get(cleanroom_class, 3520000)

    def update_contamination(self, activity_level: float, time_hours: float):
        """Update contamination based on activity"""
        # Contamination increases with activity
        contamination_rate = activity_level * 100  # particles/hour

        self.particle_count += contamination_rate * time_hours
        self.time_since_cleaning += time_hours

        # Gradual contamination even without activity
        self.particle_count *= 1.001 ** time_hours

    def calculate_yield_impact(self, process_sensitivity: float) -> float:
        """Calculate yield impact from contamination"""
        # More sensitive processes have higher impact
        base_impact = self.particle_count / 1000000  # Normalize
        
        yield_reduction = base_impact * process_sensitivity
        return max(0, 1 - yield_reduction)

    def perform_cleaning(self):
        """Perform cleanroom cleaning"""
        self.particle_count = self._get_base_particles(self.cleanroom_class)
        self.time_since_cleaning = 0

# ===============================================================================
# THERMAL MANAGEMENT
# ===============================================================================

class ThermalManagementSystem:
    """Manage heat generation and cooling"""

    def __init__(self, config):
        self.config = config
        self.ambient_temp = config["ambient_temperature"]
        self.total_heat_generation = 0
        self.cooling_capacity = 10000  # kW
        self.chiller_efficiency = 3.5  # COP

    def calculate_module_heat(self, module_states: Dict) -> float:
        """Calculate total heat generation from modules"""
        total_heat = 0
        for module_id, state in module_states.items():
            if state.spec:
                power = state.get_power_consumption()
                # Assume 80% of power becomes heat
                total_heat += power * 0.8

        return total_heat

    def calculate_cooling_requirement(self, heat_generation: float) -> float:
        """Calculate cooling power requirement"""
        # Account for building heat gain
        building_area = self.config["factory_area_m2"]
        solar_heat_gain = building_area * 0.1  # kW (simplified)

        total_heat = heat_generation + solar_heat_gain

        # COP varies with temperature differential
        target_temp = 22  # Target internal temperature
        temp_diff = self.ambient_temp - target_temp
        cop = self.chiller_efficiency - 0.05 * abs(temp_diff)
        cop = max(1.5, cop)  # Minimum COP

        cooling_power = total_heat / cop
        return cooling_power

    def check_thermal_constraints(self, heat_generation: float) -> bool:
        """Check if cooling capacity is sufficient"""
        required_cooling = self.calculate_cooling_requirement(heat_generation)
        return required_cooling <= self.cooling_capacity

# ===============================================================================
# SOFTWARE PRODUCTION SYSTEM
# ===============================================================================

class SoftwareProductionSystem:
    """Produce and manage software/firmware"""

    def __init__(self):
        self.software_library = {}
        self.development_hours = defaultdict(float)
        self.bug_rates = {
            ResourceType.PLC_PROGRAM: 0.05,
            ResourceType.ROBOT_FIRMWARE: 0.08,
            ResourceType.AI_MODEL: 0.15,
            ResourceType.SCADA_SYSTEM: 0.10
        }
        self.version_counter = defaultdict(int)

    def develop_software(self, software_type: ResourceType, dev_hours: float) -> Dict:
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

        software_package = {
            "type": software_type,
            "version": version,
            "bug_rate": bugs_after_testing,
            "lines_of_code": dev_hours * 50,  # Rough estimate
            "compatible_modules": self._get_compatible_modules(software_type)
        }

        self.software_library[f"{software_type.value}_{version}"] = software_package

        return software_package

    def _get_compatible_modules(self, software_type: ResourceType) -> List[str]:
        """Determine which modules can use this software"""
        compatibility = {
            ResourceType.PLC_PROGRAM: ["mining", "refining", "chemical", "mechanical"],
            ResourceType.ROBOT_FIRMWARE: ["cnc", "laser", "assembly", "testing"],
            ResourceType.AI_MODEL: ["transport", "recycling", "software"],
            ResourceType.SCADA_SYSTEM: ["cleanroom", "thermal", "power", "control"]
        }
        return compatibility.get(software_type, [])

    def calculate_software_reliability(self, software_type: ResourceType) -> float:
        """Calculate software reliability based on bugs"""
        if software_type not in self.bug_rates:
            return 1.0

        latest_version = f"{software_type.value}_v{self.version_counter[software_type]}.0"
        if latest_version in self.software_library:
            package = self.software_library[latest_version]
            # Reliability decreases with bug rate
            reliability = 1.0 - package["bug_rate"]
            return reliability

        return 0.95  # Default

# ===============================================================================
# Continue with the rest of the Factory class and other components...
# ===============================================================================


# ===============================================================================
# MODULE STATE - ENHANCED
# ===============================================================================

@dataclass
class ModuleState:
    """Track the ultra-realistic state of an individual module"""
    module_id: str
    module_type: str
    spec: Optional[ModuleSpec] = None
    operating_hours: float = 0.0
    cycles_completed: int = 0
    time_since_maintenance: float = 0.0
    current_efficiency: float = 1.0
    is_failed: bool = False
    is_in_maintenance: bool = False
    maintenance_end_time: float = 0.0
    current_task: Optional[str] = None
    setup_end_time: float = 0.0
    last_product_type: Optional[ResourceType] = None
    software_version: Optional[str] = None
    contamination_level: float = 0.0
    temperature: float = 22.0  # Celsius

    def update_condition(self, hours_operated: float, config: dict) -> str:
        """Update module condition after operation"""
        if not config.get("enable_degradation", True):
            return "OPERATIONAL"

        self.operating_hours += hours_operated
        self.time_since_maintenance += hours_operated

        # Random failure check
        if not self.is_failed and self.spec:
            failure_probability = hours_operated / self.spec.mtbf_hours
            if random.random() < failure_probability:
                self.is_failed = True
                return "FAILED"

        # Apply degradation
        if self.spec:
            degradation = self.spec.degradation_rate * (hours_operated / 1000)
            self.current_efficiency *= (1 - degradation)
            self.current_efficiency = max(0.3, self.current_efficiency)

            # Check for scheduled maintenance
            if config.get("enable_maintenance", True):
                if self.time_since_maintenance >= self.spec.maintenance_interval:
                    return "MAINTENANCE_REQUIRED"

        return "OPERATIONAL"

    def get_effective_throughput(self) -> float:
        """Get current throughput considering all factors"""
        if self.is_failed or self.is_in_maintenance:
            return 0.0
        if self.spec:
            base_throughput = self.spec.max_throughput * self.current_efficiency

            # Temperature derating
            if abs(self.temperature - 22) > 5:
                temp_factor = 1.0 - 0.01 * abs(self.temperature - 22)
                base_throughput *= temp_factor

            # Software reliability impact
            if self.software_version:
                # Simplified - would connect to SoftwareProductionSystem
                base_throughput *= 0.95

            return base_throughput
        return float('inf')

    def get_power_consumption(self) -> float:
        """Get current power consumption"""
        if not self.spec:
            return 0.0
        if self.is_failed:
            return 0.0
        if self.is_in_maintenance:
            return self.spec.power_consumption_idle * 0.5
        if self.current_task:
            return self.spec.power_consumption_active
        return self.spec.power_consumption_idle

# ===============================================================================
# STORAGE SYSTEM - ENHANCED
# ===============================================================================

@dataclass
class StorageSystem:
    """Ultra-realistic storage with physical constraints and contamination"""
    total_volume_m3: float
    total_weight_capacity_tons: float
    current_inventory: Dict[ResourceType, float] = field(default_factory=dict)
    waste_inventory: Dict[ResourceType, float] = field(default_factory=dict)
    enabled: bool = True
    temperature_controlled: bool = True
    contamination_controlled: bool = True

    # Enhanced material properties
    MATERIAL_PROPERTIES = {
        # Format: (density tons/m³, storage_temp_C, sensitivity_to_contamination 0-1)
        ResourceType.SILICON_ORE: (2.3, 25, 0.1),
        ResourceType.IRON_ORE: (4.0, 25, 0.1),
        ResourceType.SILICON_WAFER: (2.3, 22, 1.0),
        ResourceType.INTEGRATED_CIRCUIT: (0.2, 22, 1.0),
        ResourceType.CHEMICAL_PUMP: (5.0, 25, 0.3),
        ResourceType.LITHIUM_COMPOUND: (1.5, 20, 0.8),
        ResourceType.SULFURIC_ACID: (1.8, 15, 0.5),
        ResourceType.ORGANIC_SOLVENT: (0.8, 10, 0.6),
    }

    def get_material_properties(self, resource: ResourceType) -> Tuple[float, float, float]:
        """Get material properties with defaults"""
        return self.MATERIAL_PROPERTIES.get(resource, (1.0, 25, 0.5))

    def can_store(self, resource: ResourceType, quantity: float) -> Tuple[bool, str]:
        """Check if storage is available with reason"""
        if not self.enabled:
            return (True, "OK")

        density, req_temp, contamination = self.get_material_properties(resource)
        volume_needed = quantity / density

        current_volume = sum(q/self.get_material_properties(r)[0] 
                           for r, q in self.current_inventory.items())
        current_weight = sum(self.current_inventory.values())

        if (current_volume + volume_needed) > self.total_volume_m3:
            return (False, "VOLUME_EXCEEDED")
            
        if (current_weight + quantity) > self.total_weight_capacity_tons:
            return (False, "WEIGHT_EXCEEDED")

        # Check temperature compatibility
        if self.temperature_controlled:
            for stored_resource in self.current_inventory:
                stored_temp = self.get_material_properties(stored_resource)[1]
                if abs(stored_temp - req_temp) > 10:
                    return (False, "TEMPERATURE_INCOMPATIBLE")

        return (True, "OK")

    def add_resource(self, resource: ResourceType, quantity: float) -> bool:
        """Add resource to storage if space available"""
        can_store, reason = self.can_store(resource, quantity)
        if not can_store:
            return False

        if resource not in self.current_inventory:
            self.current_inventory[resource] = 0
        self.current_inventory[resource] += quantity
        return True

# ===============================================================================
# TASK SYSTEM - ENHANCED
# ===============================================================================

@dataclass
class Task:
    """Ultra-realistic production task"""
    task_id: str
    priority: int
    output: ResourceType
    quantity: float
    recipe: Recipe
    dependencies: Set[str] = field(default_factory=set)
    status: str = "queued"
    assigned_module: Optional[str] = None
    transport_jobs: List[str] = field(default_factory=list)
    
    # Processing parameters
    batch_size: float = 0
    setup_time: float = 0
    process_time: float = 0
    quality_yield: float = 0.95
    contamination_impact: float = 1.0
    tolerance_achieved: Optional[float] = None
    
    # Tracking
    start_time: Optional[float] = None
    completion_time: float = 0
    actual_output: float = 0
    waste_generated: Dict[ResourceType, float] = field(default_factory=dict)
    energy_consumed: float = 0
    software_reliability: float = 1.0

# ===============================================================================
# MAIN FACTORY CLASS - ULTRA REALISTIC
# ===============================================================================

class Factory:
    """Ultra-realistic self-replicating factory with all systems"""

    def __init__(self, config=None, spec_dict=None, resource_enum=None):
        # Validate configuration using Pydantic models
        from config_validation import validate_config
        from pydantic import ValidationError

        config_dict = config or CONFIG

        try:
            validated_config = validate_config(config_dict)
            # Convert back to dict for compatibility with existing code
            self.config = validated_config.to_dict()
        except ValidationError as e:
            # Re-raise with clearer error message
            from exceptions import InvalidConfigurationError
            errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
            raise InvalidConfigurationError(
                "config",
                config_dict,
                f"Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            )
        except Exception as e:
            # Handle other validation errors
            from exceptions import InvalidConfigurationError
            raise InvalidConfigurationError(
                "config",
                config_dict,
                f"Unexpected validation error: {str(e)}"
            )

        self.time = 0.0
        self.task_counter = 0
        self.spec_dict = spec_dict
        self.resource_enum = resource_enum

        # Logging
        self.log_entries = []

        # Module management
        self.module_states: Dict[str, ModuleState] = {}

        # Initialize systems - use dynamic if spec provided, otherwise default
        if spec_dict and resource_enum and 'subsystem_data' in spec_dict:
            # Use dynamic subsystems from spec
            from dynamic_subsystems import SubsystemFactory
            subsystem_factory = SubsystemFactory(spec=spec_dict, resource_enum=resource_enum)
            self.transport_system = TransportSystem(self.config)  # Keep default for now
            self.waste_stream = subsystem_factory.create_waste_stream()
            self.software_system = subsystem_factory.create_software_system()
            self.thermal_system = ThermalManagementSystem(self.config)  # Keep default for now
            self.cleanroom_environments = {}

            # Now initialize modules (after systems are ready)
            self.initialize_modules()

            # Storage system with dynamic configuration
            self.storage = subsystem_factory.create_storage_system(
                total_volume_m3=self.config["max_storage_volume_m3"],
                total_weight_capacity_tons=self.config["max_storage_weight_tons"]
            )
        else:
            # Use default subsystems for backward compatibility
            self.transport_system = TransportSystem(self.config)
            self.waste_stream = WasteStream()
            self.software_system = SoftwareProductionSystem()
            self.thermal_system = ThermalManagementSystem(self.config)
            self.cleanroom_environments = {}

            # Now initialize modules (after systems are ready)
            self.initialize_modules()

            # Storage system
            self.storage = StorageSystem(
                total_volume_m3=self.config["max_storage_volume_m3"],
                total_weight_capacity_tons=self.config["max_storage_weight_tons"],
                enabled=self.config.get("enable_storage_limits", True)
            )

        # Energy system  
        self.energy_system = EnergySystem(self.config)

        # Task management
        self.task_queue = []
        self.active_tasks: Dict[str, Task] = {}
        self.completed_tasks = []
        self.completed_task_ids: Set[str] = set()  # O(1) lookup for dependency checking
        self.blocked_tasks: Dict[str, Task] = {}

        # Metrics tracking
        self.last_metric_time = 0.0  # Track last metric collection for efficiency
        self.init_metrics()

    def initialize_modules(self):
        """Initialize all module types with ultra-realistic states"""
        # All module types we need for ultra-realistic factory
        module_types = ["mining", "refining", "chemical", "electronics", 
                       "mechanical", "cnc", "laser", "cleanroom",
                       "assembly", "software", "transport", "recycling",
                       "testing", "thermal"]

        for module_type in module_types:
            module_id = f"{module_type}_001"
            if module_type in MODULE_SPECS:
                spec = MODULE_SPECS[module_type]
                self.module_states[module_id] = ModuleState(
                    module_id=module_id,
                    module_type=module_type,
                    spec=spec
                )

                # Initialize cleanroom environment if applicable
                if spec.cleanroom_capable:
                    self.cleanroom_environments[module_id] = CleanRoomEnvironment(
                        spec.cleanroom_capable
                    )
            else:
                # Fallback for any missing specs
                self.module_states[module_id] = ModuleState(
                    module_id=module_id,
                    module_type=module_type,
                    spec=None
                )

            self.log(f"Initialized module {module_id}")

    def init_metrics(self):
        """Initialize comprehensive metrics"""
        self.metrics = {
            "time": [],
            "energy_generated": [],
            "energy_consumed": [],
            "battery_charge": [],
            "storage_utilization": [],
            "waste_generated": [],
            "transport_jobs": [],
            "software_bugs": [],
            "thermal_load": [],
            "contamination": [],
            "module_efficiency": [],
            "quality_rate": [],
            "tasks_completed": [],
            "tasks_failed": [],
            "active_tasks": [],
            "blocked_tasks": [],
            "modules": []
        }

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging"""
        entry = {
            "timestamp": self.time,
            "level": level,
            "message": message,
            "thermal_load": self.thermal_system.calculate_module_heat(self.module_states),
            "waste_total": self.waste_stream.get_total_waste()
        }
        self.log_entries.append(entry)

        if len(self.log_entries) > MAX_LOG_ENTRIES:
            self.log_entries = self.log_entries[-LOG_TRIM_SIZE:]

    def create_production_task(self, output: ResourceType, quantity: float,
                              priority: int = 100, _visited: Optional[Set[ResourceType]] = None) -> Optional[Task]:
        """Create ultra-realistic production task with all constraints

        Args:
            output: The resource to produce
            quantity: Amount to produce
            priority: Task priority (lower = higher priority)
            _visited: Internal set for circular dependency detection

        Returns:
            Task if successfully created, None otherwise

        Raises:
            CircularDependencyError: If circular dependency detected in recipe graph
        """
        # Initialize visited set for cycle detection
        if _visited is None:
            _visited = set()

        # Check for circular dependency
        if output in _visited:
            from exceptions import CircularDependencyError
            cycle_path = [r.value for r in _visited] + [output.value]
            raise CircularDependencyError(cycle_path)

        # Add current resource to visited set
        _visited.add(output)

        try:
            # Find recipe
            recipe = next((r for r in RECIPES if r.output == output), None)
            if not recipe:
                self.log(f"No recipe found for {output.value}", "ERROR")
                return None

            # Check storage capacity
            can_store, reason = self.storage.can_store(output, quantity)
            if not can_store:
                self.log(f"Cannot store {quantity} {output.value}: {reason}", "WARNING")
                return None

            # Create task
            self.task_counter += 1
            task_id = f"task_{self.task_counter:05d}_{output.value}"

            task = Task(
                task_id=task_id,
                priority=priority,
                output=output,
                quantity=quantity,
                recipe=recipe
            )

            # Check for required inputs and create dependency tasks
            for input_resource, input_qty in recipe.inputs.items():
                required = input_qty * quantity / recipe.output_quantity

                available = self.storage.current_inventory.get(input_resource, 0)
                # Check recycled materials
                if input_resource in self.waste_stream.recyclable_materials:
                    available += self.waste_stream.process_recycling(input_resource, required)

                if available < required:
                    deficit = required - available
                    # Create dependency task with buffer (pass visited set for cycle detection)
                    dep_task = self.create_production_task(
                        input_resource,
                        deficit * 1.1,
                        priority + 1,
                        _visited=_visited.copy()  # Pass copy to allow backtracking
                    )
                    if dep_task:
                        task.dependencies.add(dep_task.task_id)

            # Check if software is required
            if recipe.software_required:
                if recipe.software_required not in self.software_system.software_library:
                    # Need to produce software first (pass visited set for cycle detection)
                    sw_task = self.create_production_task(
                        recipe.software_required,
                        1,
                        priority + 2,
                        _visited=_visited.copy()  # Pass copy to allow backtracking
                    )
                    if sw_task:
                        task.dependencies.add(sw_task.task_id)

            heapq.heappush(self.task_queue, (task.priority, task.task_id, task))
            self.log(f"Created task {task_id} for {quantity} {output.value}")

            return task
        finally:
            # Remove from visited set (backtracking)
            _visited.discard(output)

    def find_available_module(self, module_type: str) -> Optional[str]:
        """Find an available module considering all constraints"""
        suitable_modules = []

        for module_id, state in self.module_states.items():
            if (state.module_type == module_type and
                not state.is_failed and
                not state.is_in_maintenance and
                state.current_task is None):

                # Check thermal constraints
                heat = self.thermal_system.calculate_module_heat({module_id: state})
                if not self.thermal_system.check_thermal_constraints(heat):
                    continue

                suitable_modules.append((state.current_efficiency, module_id))

        if suitable_modules:
            # Return most efficient module
            suitable_modules.sort(reverse=True)
            return suitable_modules[0][1]

        return None

    def calculate_production_parameters(self, task: Task, module_state: ModuleState) -> Optional[Dict]:
        """Calculate ultra-realistic production parameters"""

        result = {
            "setup_time": 0,
            "process_time": 0,
            "total_time": 0,
            "energy_required": 0,
            "expected_yield": 0,
            "transport_time": 0,
            "waste_generated": {}
        }

        if not module_state.spec:
            # Simplified calculation for modules without specs
            result["process_time"] = task.recipe.time_hours * task.quantity / task.recipe.output_quantity
            result["total_time"] = result["process_time"]
            result["energy_required"] = task.recipe.energy_kwh * task.quantity / task.recipe.output_quantity
            result["expected_yield"] = task.quantity
            return result

        # Setup time for product changeover
        if module_state.last_product_type != task.output:
            result["setup_time"] = module_state.spec.setup_time
            module_state.last_product_type = task.output

        # Batch processing constraints
        if self.config.get("enable_batch_processing", True):
            batch_size = max(
                module_state.spec.min_batch_size,
                min(task.quantity, module_state.spec.max_batch_size)
            )
        else:
            batch_size = task.quantity

        # Calculate process time
        effective_throughput = module_state.get_effective_throughput()
        if effective_throughput <= 0:
            return None

        result["process_time"] = batch_size / effective_throughput

        # Apply tolerance constraints if applicable
        if task.recipe.tolerance_um and module_state.spec.tolerance_capability:
            if module_state.spec.tolerance_capability > task.recipe.tolerance_um:
                # Can't achieve required precision
                self.log(f"Module {module_state.module_id} cannot achieve {task.recipe.tolerance_um}μm tolerance", "WARNING")
                return None

        # Apply cleanroom constraints
        if task.recipe.cleanroom_class:
            if module_state.module_id in self.cleanroom_environments:
                cleanroom = self.cleanroom_environments[module_state.module_id]
                if cleanroom.cleanroom_class > task.recipe.cleanroom_class:
                    self.log(f"Module {module_state.module_id} cleanroom class {cleanroom.cleanroom_class} insufficient", "WARNING")
                    return None

                # Calculate contamination impact on yield
                process_sensitivity = 1.0 / task.recipe.cleanroom_class
                contamination_yield = cleanroom.calculate_yield_impact(process_sensitivity)
                task.contamination_impact = contamination_yield
            else:
                return None  # No cleanroom available

        # Quality and waste calculation
        base_quality = module_state.spec.quality_base_rate
        efficiency_factor = module_state.current_efficiency

        # Quality degrades with poor equipment and contamination
        quality_rate = base_quality * efficiency_factor * task.contamination_impact

        # Software reliability impact
        if module_state.software_version:
            sw_reliability = self.software_system.calculate_software_reliability(
                task.recipe.software_required or ResourceType.PLC_PROGRAM
            )
            quality_rate *= sw_reliability
            task.software_reliability = sw_reliability

        # Add random variation
        quality_rate *= random.gauss(1.0, 0.02)
        quality_rate = max(0.5, min(1.0, quality_rate))

        result["expected_yield"] = batch_size * quality_rate

        # Calculate waste
        waste_amount = batch_size * (1 - quality_rate)
        if waste_amount > 0:
            # Determine waste type based on output
            if task.output in [ResourceType.STEEL, ResourceType.ALUMINUM_SHEET]:
                result["waste_generated"][task.output] = waste_amount * 0.8  # 80% recyclable
            else:
                result["waste_generated"][ResourceType.PLASTIC] = waste_amount * 0.2  # Generic waste

        # Energy calculation
        setup_energy = module_state.spec.power_consumption_idle * result["setup_time"]
        process_energy = module_state.spec.power_consumption_active * result["process_time"]
        result["energy_required"] = setup_energy + process_energy

        result["total_time"] = result["setup_time"] + result["process_time"]

        return result

    def process_task(self, task: Task) -> bool:
        """Process task with ultra-realistic constraints"""

        # Check dependencies
        if task.dependencies:
            incomplete = any(
                dep_id not in [t.task_id for t in self.completed_tasks]
                for dep_id in task.dependencies
            )
            if incomplete:
                task.status = "blocked_dependencies"
                self.blocked_tasks[task.task_id] = task
                return False

        # Find suitable module
        required_module = task.recipe.required_module or "assembly"
        module_id = self.find_available_module(required_module)

        if not module_id:
            task.status = "blocked_module"
            self.blocked_tasks[task.task_id] = task
            self.log(f"Task {task.task_id} blocked - no {required_module} available")
            return False

        module_state = self.module_states[module_id]

        # Calculate production parameters
        production_params = self.calculate_production_parameters(task, module_state)
        if not production_params:
            task.status = "blocked_constraints"
            self.blocked_tasks[task.task_id] = task
            return False

        # Check thermal constraints before starting
        projected_heat = self.thermal_system.calculate_module_heat(self.module_states)
        if not self.thermal_system.check_thermal_constraints(projected_heat):
            task.status = "blocked_thermal"
            self.blocked_tasks[task.task_id] = task
            self.log(f"Task {task.task_id} blocked - thermal constraints exceeded")
            return False

        # Check energy availability
        energy_available = (
            self.energy_system.battery_charge_kwh +
            self.energy_system.calculate_solar_generation(
                self.time % 24,
                int(self.time / 24)
            ) * production_params["total_time"]
        )

        if energy_available < production_params["energy_required"]:
            task.status = "blocked_energy"
            self.blocked_tasks[task.task_id] = task
            self.log(f"Task {task.task_id} blocked - insufficient energy")
            return False

        # Check and schedule material transport
        for input_resource, input_qty in task.recipe.inputs.items():
            required = input_qty * task.quantity / task.recipe.output_quantity
            
            # Schedule transport from storage to module
            transport_job = self.transport_system.schedule_transport(
                "storage",
                module_state.module_type,
                input_resource,
                required,
                task.priority + 10
            )
            
            if transport_job:
                task.transport_jobs.append(transport_job.job_id)
                production_params["transport_time"] = max(
                    production_params["transport_time"],
                    transport_job.distance / self.transport_system.conveyor_speed / 3600
                )

        # Check input materials (after transport)
        for input_resource, input_qty in task.recipe.inputs.items():
            required = input_qty * task.quantity / task.recipe.output_quantity
            available = self.storage.current_inventory.get(input_resource, 0)

            if available < required:
                task.status = "blocked_resources"
                self.blocked_tasks[task.task_id] = task
                self.log(f"Task {task.task_id} blocked - needs {required} {input_resource.value}")
                return False

        # All checks passed - start production
        task.status = "active"
        task.assigned_module = module_id
        task.setup_time = production_params["setup_time"]
        task.process_time = production_params["process_time"]
        task.start_time = self.time
        task.completion_time = self.time + production_params["total_time"] + production_params["transport_time"]
        task.energy_consumed = production_params["energy_required"]
        task.actual_output = production_params["expected_yield"]
        task.waste_generated = production_params["waste_generated"]

        module_state.current_task = task.task_id
        module_state.setup_end_time = self.time + task.setup_time

        # Consume inputs
        for input_resource, input_qty in task.recipe.inputs.items():
            required = input_qty * task.quantity / task.recipe.output_quantity
            self.storage.current_inventory[input_resource] -= required

        # Consume energy
        self.energy_system.update_battery(
            -production_params["energy_required"],
            production_params["total_time"]
        )

        self.active_tasks[task.task_id] = task
        self.log(f"Started task {task.task_id} on {module_id} (ETA: {task.completion_time:.1f}h)")

        return True

    def update_active_tasks(self):
        """Update active tasks with all systems"""
        completed_this_step = []

        for task_id, task in list(self.active_tasks.items()):
            if self.time >= task.completion_time:
                # Task completed
                module_id = task.assigned_module
                module_state = self.module_states[module_id]

                # Update module condition
                hours_operated = task.setup_time + task.process_time
                condition = module_state.update_condition(hours_operated, self.config)

                # Update cleanroom contamination if applicable
                if module_id in self.cleanroom_environments:
                    cleanroom = self.cleanroom_environments[module_id]
                    activity_level = task.quantity / 100  # Normalized
                    cleanroom.update_contamination(activity_level, hours_operated)

                # Add waste to stream
                for waste_type, waste_qty in task.waste_generated.items():
                    self.waste_stream.add_waste(waste_type, waste_qty)

                # Schedule output transport to storage
                output_transport = self.transport_system.schedule_transport(
                    module_state.module_type,
                    "storage",
                    task.output,
                    task.actual_output,
                    50  # Lower priority for output
                )

                # Add output to storage
                if self.storage.add_resource(task.output, task.actual_output):
                    task.status = "completed"
                    self.completed_tasks.append(task)
                    self.completed_task_ids.add(task_id)  # Add to set for O(1) lookup
                    self.log(f"Completed task {task_id}: {task.actual_output:.1f} {task.output.value}")

                    # Check if this produces a new module
                    if task.output.value.endswith("_module"):
                        module_type = task.output.value.replace("_module", "")
                        new_module_id = f"{module_type}_{len([m for m in self.module_states if m.startswith(module_type)])+1:03d}"

                        if module_type in MODULE_SPECS:
                            self.module_states[new_module_id] = ModuleState(
                                module_id=new_module_id,
                                module_type=module_type,
                                spec=MODULE_SPECS[module_type]
                            )
                            
                            # Initialize cleanroom if applicable
                            if MODULE_SPECS[module_type].cleanroom_capable:
                                self.cleanroom_environments[new_module_id] = CleanRoomEnvironment(
                                    MODULE_SPECS[module_type].cleanroom_capable
                                )
                        else:
                            self.module_states[new_module_id] = ModuleState(
                                module_id=new_module_id,
                                module_type=module_type,
                                spec=None
                            )
                        self.log(f"New module created: {new_module_id}")

                    # Check if this is software
                    if task.output in [ResourceType.PLC_PROGRAM, ResourceType.ROBOT_FIRMWARE,
                                       ResourceType.AI_MODEL, ResourceType.SCADA_SYSTEM]:
                        sw_package = self.software_system.develop_software(
                            task.output,
                            task.process_time
                        )
                        self.log(f"Software developed: {task.output.value} {sw_package['version']}")
                else:
                    self.log(f"Task {task_id} output rejected - storage full", "WARNING")

                # Free up module
                module_state.current_task = None

                # Check module condition
                if condition == "FAILED":
                    module_state.is_failed = True
                    self.log(f"Module {module_id} has FAILED!", "ERROR")
                elif condition == "MAINTENANCE_REQUIRED":
                    self.schedule_maintenance(module_id)

                completed_this_step.append(task_id)

        # Remove completed tasks
        for task_id in completed_this_step:
            del self.active_tasks[task_id]

    def schedule_maintenance(self, module_id: str):
        """Schedule maintenance for a module"""
        if not self.config.get("enable_maintenance", True):
            return

        module_state = self.module_states[module_id]
        if not module_state.is_in_maintenance:
            maintenance_duration = 8.0  # hours
            module_state.is_in_maintenance = True
            module_state.maintenance_end_time = self.time + maintenance_duration
            self.log(f"Module {module_id} entering maintenance until {module_state.maintenance_end_time:.1f}")

    def update_maintenance(self):
        """Update maintenance status"""
        for module_id, module_state in self.module_states.items():
            if module_state.is_in_maintenance:
                if self.time >= module_state.maintenance_end_time:
                    module_state.is_in_maintenance = False
                    module_state.time_since_maintenance = 0
                    module_state.current_efficiency = min(1.0, module_state.current_efficiency * 1.1)
                    self.log(f"Module {module_id} maintenance completed")

    def check_blocked_tasks(self):
        """Re-evaluate blocked tasks with O(1) dependency checking"""
        unblocked = []

        for task_id, task in self.blocked_tasks.items():
            should_retry = False

            if task.status == "blocked_dependencies":
                # Use set for O(1) lookup instead of O(n) list search
                deps_complete = all(
                    dep_id in self.completed_task_ids
                    for dep_id in task.dependencies
                )
                should_retry = deps_complete

            elif task.status in ["blocked_module", "blocked_energy", "blocked_resources", 
                               "blocked_thermal", "blocked_constraints"]:
                # Retry periodically
                should_retry = True

            if should_retry:
                task.status = "queued"
                heapq.heappush(self.task_queue, (task.priority, task.task_id, task))
                unblocked.append(task_id)

        for task_id in unblocked:
            del self.blocked_tasks[task_id]

    def collect_metrics(self):
        """Collect comprehensive metrics efficiently"""
        # Only collect every hour (more efficient than modulo check every step)
        if self.time - self.last_metric_time < 1.0:
            return

        self.last_metric_time = self.time

        if True:  # Keep indentation for rest of method
            # Module efficiency
            avg_efficiency = sum(
                m.current_efficiency for m in self.module_states.values()
            ) / len(self.module_states) if self.module_states else 0

            # Thermal load
            thermal_load = self.thermal_system.calculate_module_heat(self.module_states)

            # Storage utilization  
            storage_volume = sum(
                q/self.storage.get_material_properties(r)[0]
                for r, q in self.storage.current_inventory.items()
            )
            storage_util = storage_volume / self.storage.total_volume_m3 if self.storage.enabled else 0

            # Software bugs
            total_bugs = sum(
                pkg.get("bug_rate", 0) 
                for pkg in self.software_system.software_library.values()
            )

            # Average contamination
            avg_contamination = 0
            if self.cleanroom_environments:
                avg_contamination = sum(
                    cr.particle_count for cr in self.cleanroom_environments.values()
                ) / len(self.cleanroom_environments)

            self.metrics["time"].append(self.time)
            self.metrics["energy_generated"].append(
                self.energy_system.calculate_solar_generation(
                    self.time % 24, int(self.time / 24)
                )
            )
            self.metrics["battery_charge"].append(self.energy_system.battery_charge_kwh)
            self.metrics["storage_utilization"].append(storage_util)
            self.metrics["waste_generated"].append(self.waste_stream.get_total_waste())
            self.metrics["transport_jobs"].append(len(self.transport_system.active_transports))
            self.metrics["software_bugs"].append(total_bugs)
            self.metrics["thermal_load"].append(thermal_load)
            self.metrics["contamination"].append(avg_contamination)
            self.metrics["module_efficiency"].append(avg_efficiency)
            self.metrics["tasks_completed"].append(len(self.completed_tasks))
            self.metrics["active_tasks"].append(len(self.active_tasks))
            self.metrics["blocked_tasks"].append(len(self.blocked_tasks))
            self.metrics["modules"].append(len(self.module_states))

    def simulate_step(self, duration_hours: float = 0.1):
        """Single ultra-realistic simulation step"""

        # Update energy
        hour_of_day = self.time % 24
        day_of_year = int(self.time / 24) % 365

        solar_generation = self.energy_system.calculate_solar_generation(hour_of_day, day_of_year)

        # Account for all power consumption
        total_consumption = sum(m.get_power_consumption() for m in self.module_states.values())
        
        # Add cooling power
        thermal_load = self.thermal_system.calculate_module_heat(self.module_states)
        cooling_power = self.thermal_system.calculate_cooling_requirement(thermal_load)
        total_consumption += cooling_power

        # Add transport power
        transport_power = len(self.transport_system.active_transports) * TRANSPORT_POWER_KW_PER_ACTIVE
        total_consumption += transport_power

        net_energy = (solar_generation - total_consumption) * duration_hours
        self.energy_system.update_battery(net_energy, duration_hours)

        # Update transport system
        self.transport_system.process_transport_queue(self.time)
        self.transport_system.update_active_transports(self.time)
        self.transport_system.maintain_agvs(self.time)

        # Update active tasks
        self.update_active_tasks()

        # Update maintenance
        self.update_maintenance()

        # Clean rooms periodically
        if int(self.time) % WEEKLY_CLEANING_INTERVAL_HOURS == 0:  # Weekly
            for cleanroom in self.cleanroom_environments.values():
                if cleanroom.time_since_cleaning > WEEKLY_CLEANING_INTERVAL_HOURS:
                    cleanroom.perform_cleaning()
                    self.log("Cleanroom cleaned")

        # Process new tasks
        tasks_started = 0

        while self.task_queue and tasks_started < MAX_TASK_STARTS_PER_STEP:
            priority, task_id, task = heapq.heappop(self.task_queue)

            if self.process_task(task):
                tasks_started += 1

        # Check blocked tasks periodically
        if int(self.time * 10) % 10 == 0:
            self.check_blocked_tasks()

        # Collect metrics
        self.collect_metrics()

        # Advance time
        self.time += duration_hours

        # Age equipment
        self.energy_system.panel_age_days += duration_hours / 24
        if self.config.get("enable_weather", True):
            self.energy_system.days_since_cleaning += duration_hours / 24

    def run_simulation(self, max_hours: float = 10000, max_wall_time_seconds: float = 3600) -> Dict:
        """Run ultra-realistic simulation with wall-clock timeout protection

        Args:
            max_hours: Maximum simulation time in hours
            max_wall_time_seconds: Maximum real-world execution time in seconds (default: 1 hour)

        Returns:
            Simulation results dictionary

        Raises:
            SimulationTimeoutError: If wall-clock time limit exceeded
        """
        import time
        from exceptions import SimulationTimeoutError

        start_wall_time = time.time()

        print("=" * 80)
        print("ULTRA-REALISTIC SELF-REPLICATING FACTORY SIMULATION")
        print("=" * 80)
        print("\nConfiguration:")
        print(f"  Factory Area: {self.config['factory_area_m2']:,} m²")
        print(f"  Storage Capacity: {self.config['max_storage_volume_m3']:,} m³")
        print(f"  AGV Fleet Size: {self.config['agv_fleet_size']}")
        print(f"  Clean Room Class: {self.config['cleanroom_class']}")
        print(f"  All realistic features: ENABLED")
        print(f"  Wall-clock timeout: {max_wall_time_seconds:.0f} seconds")

        print("\n🏭 STARTING ULTRA-REALISTIC FACTORY REPLICATION")
        print("-" * 40)

        # Create production tasks for all factory modules
        if self.spec_dict and 'target_modules' in self.spec_dict and self.spec_dict['target_modules']:
            # Use modules defined in spec
            module_types = []
            for module_name in self.spec_dict['target_modules']:
                if hasattr(self.resource_enum, module_name):
                    module_types.append(getattr(self.resource_enum, module_name))
                else:
                    print(f"  Warning: Module {module_name} not found in resource enum")
        else:
            # Use default module list for backward compatibility
            module_types = [
                ResourceType.MINING_MODULE,
                ResourceType.REFINING_MODULE,
                ResourceType.CHEMICAL_MODULE,
                ResourceType.ELECTRONICS_MODULE,
                ResourceType.MECHANICAL_MODULE,
                ResourceType.CNC_MODULE,
                ResourceType.LASER_MODULE,
                ResourceType.CLEANROOM_MODULE,
                ResourceType.ASSEMBLY_MODULE,
                ResourceType.SOFTWARE_MODULE,
                ResourceType.TRANSPORT_MODULE,
                ResourceType.RECYCLING_MODULE,
                ResourceType.TESTING_MODULE,
                ResourceType.THERMAL_MODULE,
                ResourceType.POWER_MODULE,
                ResourceType.CONTROL_MODULE
            ]

        for module in module_types:
            task = self.create_production_task(module, 1, priority=1)
            if task:
                print(f"  Created task for {module.value}")

        # Main simulation loop
        print("\n⏱️ SIMULATION PROGRESS")
        print("-" * 40)

        last_report = 0
        while self.time < max_hours:
            # Check wall-clock timeout
            elapsed_wall_time = time.time() - start_wall_time
            if elapsed_wall_time > max_wall_time_seconds:
                raise SimulationTimeoutError(
                    self.time,
                    max_hours
                )

            self.simulate_step(0.1)

            # Progress report at regular intervals
            if self.time - last_report >= PROGRESS_REPORT_INTERVAL_HOURS:
                last_report = self.time

                # Calculate comprehensive metrics
                active = len(self.active_tasks)
                blocked = len(self.blocked_tasks)
                completed = len(self.completed_tasks)
                modules_count = len(self.module_states)
                transport_active = len(self.transport_system.active_transports)
                waste_total = self.waste_stream.get_total_waste()

                # Module health
                failed_modules = sum(1 for m in self.module_states.values() if m.is_failed)
                avg_efficiency = sum(
                    m.current_efficiency for m in self.module_states.values()
                ) / modules_count if modules_count > 0 else 0

                print(f"\nTime: {self.time:.1f} hours ({self.time/24:.1f} days)")
                print(f"  Tasks: {active} active, {blocked} blocked, {completed} completed")
                print(f"  Modules: {modules_count} total, {failed_modules} failed")
                print(f"  Transport: {transport_active} jobs active")
                print(f"  Waste: {waste_total:.1f} tons total")
                print(f"  Avg Efficiency: {avg_efficiency:.1%}")
                print(f"  Battery: {self.energy_system.battery_charge_kwh:.1f} kWh")

                # Check if all module tasks are complete
                module_tasks_complete = all(
                    any(t.output == module and t.status == "completed"
                        for t in self.completed_tasks)
                    for module in module_types
                )

                if module_tasks_complete:
                    print("\n✅ ULTRA-REALISTIC REPLICATION COMPLETE!")
                    break

                # Check if stuck
                if active == 0 and len(self.task_queue) == 0 and blocked > 0:
                    print("\n⚠️ SIMULATION STUCK - Blocked tasks cannot proceed")
                    # Print blocked reasons
                    blocked_reasons = defaultdict(int)
                    for task in self.blocked_tasks.values():
                        blocked_reasons[task.status] += 1
                    for reason, count in blocked_reasons.items():
                        print(f"    {reason}: {count} tasks")
                    break

        # Final report
        return self.generate_final_report()

    def generate_final_report(self) -> Dict:
        """Generate comprehensive final report"""
        print("\n" + "=" * 80)
        print("ULTRA-REALISTIC SIMULATION - FINAL REPORT")
        print("=" * 80)

        print(f"\nTotal Simulation Time: {self.time:.1f} hours ({self.time/24:.1f} days)")
        print(f"Total Tasks Completed: {len(self.completed_tasks)}")

        print("\nModule Production Summary:")
        module_counts = defaultdict(int)
        for task in self.completed_tasks:
            if task.output.value.endswith("_module"):
                module_counts[task.output.value] += int(task.actual_output)

        for module, count in sorted(module_counts.items()):
            print(f"  {module:25}: {count}")

        print(f"\nWaste Generated: {self.waste_stream.get_total_waste():.1f} tons")
        print(f"Transport Jobs Completed: {len(self.transport_system.completed_transports)}")
        print(f"Software Packages Developed: {len(self.software_system.software_library)}")

        # Calculate material efficiency
        total_input = sum(self.storage.current_inventory.values())
        total_waste = self.waste_stream.get_total_waste()
        if total_input + total_waste > 0:
            material_efficiency = total_input / (total_input + total_waste)
            print(f"Material Efficiency: {material_efficiency:.1%}")

        # Save results
        results = {
            "config": self.config,
            "final_status": {
                "time": self.time,
                "completed_tasks": len(self.completed_tasks),
                "active_tasks": len(self.active_tasks),
                "blocked_tasks": len(self.blocked_tasks),
                "modules": {
                    module_type: sum(
                        1 for m in self.module_states.values()
                        if m.module_type == module_type and not m.is_failed
                    )
                    for module_type in MODULE_SPECS.keys()
                },
                "waste_total": self.waste_stream.get_total_waste(),
                "transport_completed": len(self.transport_system.completed_transports),
                "software_packages": len(self.software_system.software_library)
            },
            "metrics": self.metrics,
            "completed_tasks": [
                {
                    "task_id": t.task_id,
                    "output": t.output.value,
                    "quantity": t.quantity,
                    "actual_output": t.actual_output,
                    "energy_consumed": t.energy_consumed,
                    "completion_time": t.completion_time,
                    "quality_yield": t.actual_output / t.quantity if t.quantity > 0 else 0,
                    "waste_generated": {k.value: v for k, v in t.waste_generated.items()}
                }
                for t in self.completed_tasks[-100:]
            ],
            "log_entries": self.log_entries[-1000:]
        }

        with open("factory_simulation_log.json", "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📊 Results saved to factory_simulation_log.json")

        return results

# ===============================================================================
# ENERGY SYSTEM (from original)
# ===============================================================================

class EnergySystem:
    """Energy system with realistic constraints"""

    def __init__(self, config):
        self.config = config
        self.solar_capacity_kw = config["initial_solar_capacity_kw"]
        self.panel_efficiency = config["solar_panel_efficiency"]
        self.battery_capacity_kwh = 1000
        self.battery_charge_kwh = self.battery_capacity_kwh * 0.5
        self.battery_cycles = 0
        self.panel_age_days = 0
        self.days_since_cleaning = 0
        self.latitude = config.get("latitude", 35)
        self.average_cloud_cover = config.get("average_cloud_cover", 0.3)

    def calculate_solar_generation(self, hour_of_day: float, day_of_year: int) -> float:
        """Calculate solar generation based on time and conditions"""
        if not self.config.get("enable_weather", True):
            return self.solar_capacity_kw * 8 / 24

        # Solar angle calculation
        hour_angle = 15 * (hour_of_day - 12)
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))

        # Zenith angle
        zenith_rad = math.acos(
            math.sin(math.radians(self.latitude)) * math.sin(math.radians(declination)) +
            math.cos(math.radians(self.latitude)) * math.cos(math.radians(declination)) *
            math.cos(math.radians(hour_angle))
        )

        # Solar irradiance
        if zenith_rad > math.pi/2:
            base_irradiance = 0
        else:
            base_irradiance = 1000 * math.cos(zenith_rad)

        # Weather factor
        weather_factor = 1.0 - self.average_cloud_cover * random.gauss(1.0, 0.2)
        weather_factor = max(0.1, min(1.0, weather_factor))

        # Panel degradation
        age_factor = 0.995 ** (self.panel_age_days / 365)

        # Dust accumulation
        dust_factor = max(0.7, 1.0 - 0.01 * self.days_since_cleaning)

        # Temperature derating
        temp = self.config.get("ambient_temperature", 25)
        temp_factor = 1.0 - 0.004 * (temp - 25)

        # Calculate actual generation
        actual_generation = (
            self.solar_capacity_kw *
            (base_irradiance / 1000) *
            weather_factor *
            age_factor *
            dust_factor *
            temp_factor
        )

        return max(0, actual_generation)

    def update_battery(self, energy_delta_kwh: float, duration_hours: float) -> float:
        """Update battery state"""
        if energy_delta_kwh > 0:
            # Charging
            charge_rate = min(energy_delta_kwh, self.battery_capacity_kwh * 0.5)
            actual_charge = charge_rate * self.config["battery_efficiency"]
            self.battery_charge_kwh = min(
                self.battery_capacity_kwh * 0.95,
                self.battery_charge_kwh + actual_charge
            )
            self.battery_cycles += actual_charge / self.battery_capacity_kwh
            return actual_charge
        else:
            # Discharging
            discharge_requested = abs(energy_delta_kwh)
            max_discharge = self.battery_capacity_kwh * 0.5
            actual_discharge = min(
                discharge_requested,
                max_discharge,
                self.battery_charge_kwh - self.battery_capacity_kwh * 0.2
            )
            self.battery_charge_kwh -= actual_discharge
            self.battery_cycles += actual_discharge / self.battery_capacity_kwh
            return -actual_discharge

    def get_battery_health(self) -> float:
        """Calculate battery health"""
        if not self.config.get("enable_degradation", True):
            return 1.0

        cycle_degradation = max(0.8, 1.0 - 0.0001 * self.battery_cycles)
        calendar_degradation = 0.95 ** (self.panel_age_days / 365)

        return cycle_degradation * calendar_degradation

# ===============================================================================
# MAIN EXECUTION
# ===============================================================================

# Default configuration - can be overridden by spec loading
RESOURCE_TYPE = ResourceType  # Default enum
MODULE_SPECS_DEFAULT = MODULE_SPECS  # Default module specs
RECIPES_DEFAULT = RECIPES  # Default recipes

def main():
    """Main entry point with spec loading support"""
    parser = argparse.ArgumentParser(
        description='Ultra-Realistic Self-Replicating Factory Simulation'
    )
    parser.add_argument('--spec', type=str, default=None,
                       help='Path to spec file (e.g., specs/minimal.spec)')
    parser.add_argument('--profile', type=str, default=None,
                       help='Configuration profile to use from spec')
    parser.add_argument('--max-hours', type=int, default=10000,
                       help='Maximum simulation hours')
    parser.add_argument('--output', type=str, default='factory_simulation_log.json',
                       help='Output file for simulation results')
    parser.add_argument('--modular', action='store_true',
                       help='Use ModularFactory with custom subsystems from spec')
    args = parser.parse_args()

    # Load configuration
    config = CONFIG.copy()
    recipes = RECIPES_DEFAULT
    module_specs = MODULE_SPECS_DEFAULT
    spec_dict = None
    resource_enum_for_factory = None

    if args.spec:
        try:
            # Try to load spec file
            from spec_loader import SpecLoader

            loader = SpecLoader()
            spec = loader.load_spec(args.spec)

            # Create dynamic ResourceType enum from spec
            global ResourceType
            ResourceType = loader.create_resource_enum(spec)
            resource_enum_for_factory = ResourceType

            # Create recipes and module specs from spec
            recipes = loader.create_recipes(spec, ResourceType)
            module_specs = loader.create_module_specs(spec)

            # Create config from spec
            config = loader.create_config(spec, args.profile)

            # Create spec dict for Factory
            spec_dict = {
                'subsystem_data': spec.subsystem_data,
                'resources': spec.resources,
                'target_modules': spec.target_modules
            }

            # Update global references
            global RECIPES, MODULE_SPECS
            RECIPES = recipes
            MODULE_SPECS = module_specs

            print(f"Loaded spec: {spec.metadata.get('name', 'Unknown')}")
            print(f"Resources: {len(spec.resources)}")
            print(f"Recipes: {len(recipes)}")
            print(f"Modules: {len(module_specs)}")
            if args.profile:
                print(f"Profile: {args.profile}")
            if spec.subsystem_data:
                print(f"Dynamic subsystems: ENABLED")
        except ImportError:
            print("Warning: spec_loader module not found, using default configuration")
        except Exception as e:
            print(f"Error loading spec: {e}")
            print("Falling back to default configuration")

    # Run simulation - use ModularFactory if --modular flag is set
    if args.modular:
        # Use ModularFactory with spec-defined subsystems
        from factory_builder import create_factory_from_spec
        from modular_framework import UpdateStrategy

        if args.spec:
            # Create from spec with subsystem implementations
            factory = create_factory_from_spec(
                args.spec,
                profile=args.profile,
                update_strategy=UpdateStrategy.SEQUENTIAL
            )
            print(f"Using ModularFactory with spec-defined subsystems")
        else:
            # Use ModularFactory with defaults
            from modular_factory_adapter import ModularFactory
            factory = ModularFactory(config)
            print(f"Using ModularFactory with default subsystems")

        results = factory.run_simulation(max_hours=args.max_hours)
    else:
        # Use traditional Factory
        factory = Factory(config, spec_dict=spec_dict, resource_enum=resource_enum_for_factory)
        results = factory.run_simulation(max_hours=args.max_hours)

    # Save results
    if results:
        with open(args.output, 'w') as f:
            json.dump(results, f)
        print(f"Simulation results saved to {args.output}")

    return results

if __name__ == "__main__":
    main()
